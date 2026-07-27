#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <mysql.h>
#include <ctype.h>

// Helper to decode URL-encoded string
void urldecode(char *dst, const char *src) {
    char a, b;
    while (*src) {
        if ((*src == '%') && ((a = src[1]) && (b = src[2])) && (isxdigit(a) && isxdigit(b))) {
            if (a >= 'a') a -= 'a'-'A'; if (a >= 'A') a -= ('A' - 10); else a -= '0';
            if (b >= 'a') b -= 'a'-'A'; if (b >= 'A') b -= ('A' - 10); else b -= '0';
            *dst++ = 16*a+b; src+=3;
        } else if (*src == '+') { *dst++ = ' '; src++; } else { *dst++ = *src++; }
    }
    *dst++ = '\0';
}

// Helper to get query parameter
void get_param(const char *query, const char *key, char *out) {
    out[0] = '\0';
    if (!query) return;
    char *q = strdup(query);
    char *pair = strtok(q, "&");
    while (pair != NULL) {
        char *eq = strchr(pair, '=');
        if (eq) {
            *eq = '\0';
            if (strcmp(pair, key) == 0) {
                urldecode(out, eq + 1);
                break;
            }
        }
        pair = strtok(NULL, "&");
    }
    free(q);
}

// Structure representing a Book record for sorting
typedef struct {
    int id;
    char title[256];
    char author[256];
    char price[64];
    char total_qty[64];
    char avail_qty[64];
} Book;

// Implementation of Bubble Sort (from the syllabus)
// Bubble Sort works by repeatedly swapping adjacent elements if they are in the wrong order.
// In this case, we sort books by their database IDs in ascending order.
void bubble_sort(Book *books, int n) {
    int i, j;
    Book temp;
    for (i = 0; i < n - 1; i++) {
        for (j = 0; j < n - i - 1; j++) {
            if (books[j].id > books[j + 1].id) {
                // Swap the two adjacent Book structures
                temp = books[j];
                books[j] = books[j + 1];
                books[j + 1] = temp;
            }
        }
    }
}

void print_json_header() {
    printf("Content-Type: application/json\n");
    printf("Access-Control-Allow-Origin: *\n\n");
}

int main() {
    print_json_header();

    char *query = getenv("QUERY_STRING");
    if (!query) {
        printf("{\"error\": \"No query string provided\"}\n");
        return 0;
    }

    MYSQL *conn = mysql_init(NULL);
    if (!mysql_real_connect(conn, "localhost", "root", "", "library_system", 0, NULL, 0)) {
        printf("{\"error\": \"Database connection failed\"}\n");
        return 0;
    }

    char action[256] = {0};
    get_param(query, "action", action);

    if (strcmp(action, "dashboard") == 0) {
        int total_books = 0, avail_books = 0, issued_books = 0, total_users = 0;
        MYSQL_RES *res; MYSQL_ROW row;
        
        mysql_query(conn, "SELECT SUM(total_quantity), SUM(available_quantity) FROM books");
        res = mysql_store_result(conn);
        if((row = mysql_fetch_row(res))) {
            total_books = row[0] ? atoi(row[0]) : 0;
            avail_books = row[1] ? atoi(row[1]) : 0;
        }
        mysql_free_result(res);

        mysql_query(conn, "SELECT COUNT(*) FROM transactions WHERE actual_return_date IS NULL");
        res = mysql_store_result(conn);
        if((row = mysql_fetch_row(res))) issued_books = atoi(row[0]);
        mysql_free_result(res);

        mysql_query(conn, "SELECT COUNT(*) FROM users");
        res = mysql_store_result(conn);
        if((row = mysql_fetch_row(res))) total_users = atoi(row[0]);
        mysql_free_result(res);

        printf("{\"total_books\": %d, \"available_books\": %d, \"issued_books\": %d, \"total_users\": %d}\n", 
               total_books, avail_books, issued_books, total_users);

    } else if (strcmp(action, "get_books") == 0) {
        mysql_query(conn, "SELECT id, title, author, price, description, total_quantity, available_quantity FROM books");
        MYSQL_RES *res = mysql_store_result(conn);
        int num_rows = mysql_num_rows(res);
        
        // Dynamically allocate memory for retrieved books
        Book *books_array = (Book *)malloc(num_rows * sizeof(Book));
        MYSQL_ROW row;
        int count = 0;
        
        // Load MySQL rows into C structures
        while ((row = mysql_fetch_row(res)) && count < num_rows) {
            books_array[count].id = atoi(row[0]);
            strncpy(books_array[count].title, row[1], 255);
            books_array[count].title[255] = '\0';
            strncpy(books_array[count].author, row[2], 255);
            books_array[count].author[255] = '\0';
            strncpy(books_array[count].price, row[3], 63);
            books_array[count].price[63] = '\0';
            strncpy(books_array[count].total_qty, row[5], 63);
            books_array[count].total_qty[63] = '\0';
            strncpy(books_array[count].avail_qty, row[6], 63);
            books_array[count].avail_qty[63] = '\0';
            count++;
        }
        mysql_free_result(res);

        // Apply Bubble Sort from syllabus to sort retrieved books by ID
        bubble_sort(books_array, count);

        // Output the sorted list of books as JSON
        printf("[");
        for (int i = 0; i < count; i++) {
            if (i > 0) printf(",");
            printf("{\"id\":%d,\"title\":\"%s\",\"author\":\"%s\",\"price\":\"%s\",\"total_qty\":\"%s\",\"avail_qty\":\"%s\"}",
                   books_array[i].id, books_array[i].title, books_array[i].author, 
                   books_array[i].price, books_array[i].total_qty, books_array[i].avail_qty);
        }
        printf("]\n");
        
        // Free dynamic memory allocation
        free(books_array);

    } else if (strcmp(action, "add_book") == 0) {
        char title[256], author[256], price[64], desc[512], qty[64];
        get_param(query, "title", title); get_param(query, "author", author);
        get_param(query, "price", price); get_param(query, "description", desc);
        get_param(query, "quantity", qty);

        char sql[1024];
        sprintf(sql, "INSERT INTO books (title, author, price, description, total_quantity, available_quantity) VALUES ('%s', '%s', %s, '%s', %s, %s)",
                title, author, price, desc, qty, qty);
        
        if (mysql_query(conn, sql)) {
            printf("{\"error\": \"%s\"}\n", mysql_error(conn));
        } else {
            printf("{\"success\": \"Book added successfully\"}\n");
        }

    } else if (strcmp(action, "get_users") == 0) {
        mysql_query(conn, "SELECT id, name, email FROM users");
        MYSQL_RES *res = mysql_store_result(conn);
        MYSQL_ROW row;
        printf("[");
        int first = 1;
        while ((row = mysql_fetch_row(res))) {
            if (!first) printf(",");
            printf("{\"id\":%s,\"name\":\"%s\",\"email\":\"%s\"}", row[0], row[1], row[2]);
            first = 0;
        }
        printf("]\n");
        mysql_free_result(res);

    } else if (strcmp(action, "add_user") == 0) {
        char name[256], email[256];
        get_param(query, "name", name); get_param(query, "email", email);

        char sql[512];
        sprintf(sql, "INSERT INTO users (name, email) VALUES ('%s', '%s')", name, email);
        if (mysql_query(conn, sql)) {
            printf("{\"error\": \"%s\"}\n", mysql_error(conn));
        } else {
            printf("{\"success\": \"User added successfully\"}\n");
        }

    } else if (strcmp(action, "issue_book") == 0) {
        char user_id[64], book_id[64], return_date[128];
        get_param(query, "user_id", user_id); get_param(query, "book_id", book_id); get_param(query, "return_date", return_date);

        // Check availability
        char check_sql[256];
        sprintf(check_sql, "SELECT available_quantity FROM books WHERE id = %s", book_id);
        mysql_query(conn, check_sql);
        MYSQL_RES *res = mysql_store_result(conn);
        MYSQL_ROW row = mysql_fetch_row(res);
        int avail = row ? atoi(row[0]) : 0;
        mysql_free_result(res);

        if (avail <= 0) {
            printf("{\"error\": \"Book is not available\"}\n");
        } else {
            char sql[1024];
            sprintf(sql, "INSERT INTO transactions (user_id, book_id, issue_date, return_date) VALUES (%s, %s, CURDATE(), '%s')", user_id, book_id, return_date);
            if (mysql_query(conn, sql)) {
                printf("{\"error\": \"%s\"}\n", mysql_error(conn));
            } else {
                sprintf(sql, "UPDATE books SET available_quantity = available_quantity - 1 WHERE id = %s", book_id);
                mysql_query(conn, sql);
                printf("{\"success\": \"Book issued successfully\"}\n");
            }
        }

    } else if (strcmp(action, "return_book") == 0) {
        char transaction_id[64];
        get_param(query, "transaction_id", transaction_id);

        char sql[512];
        // Get book ID first
        sprintf(sql, "SELECT book_id FROM transactions WHERE id = %s", transaction_id);
        mysql_query(conn, sql);
        MYSQL_RES *res = mysql_store_result(conn);
        MYSQL_ROW row = mysql_fetch_row(res);
        char book_id[64] = {0};
        if(row) strcpy(book_id, row[0]);
        mysql_free_result(res);

        if (strlen(book_id) > 0) {
            sprintf(sql, "UPDATE transactions SET actual_return_date = CURDATE() WHERE id = %s", transaction_id);
            if(mysql_query(conn, sql)) {
                 printf("{\"error\": \"%s\"}\n", mysql_error(conn));
            } else {
                sprintf(sql, "UPDATE books SET available_quantity = available_quantity + 1 WHERE id = %s", book_id);
                mysql_query(conn, sql);
                printf("{\"success\": \"Book returned successfully\"}\n");
            }
        } else {
             printf("{\"error\": \"Transaction not found\"}\n");
        }

    } else if (strcmp(action, "get_transactions") == 0) {
        char sql[] = "SELECT t.id, u.name, b.title, t.issue_date, t.return_date, t.actual_return_date "
                     "FROM transactions t JOIN users u ON t.user_id = u.id JOIN books b ON t.book_id = b.id";
        mysql_query(conn, sql);
        MYSQL_RES *res = mysql_store_result(conn);
        MYSQL_ROW row;
        printf("[");
        int first = 1;
        while ((row = mysql_fetch_row(res))) {
            if (!first) printf(",");
            printf("{\"id\":%s,\"user\":\"%s\",\"book\":\"%s\",\"issue_date\":\"%s\",\"return_date\":\"%s\",\"actual_return_date\":\"%s\"}",
                   row[0], row[1], row[2], row[3], row[4], row[5] ? row[5] : "");
            first = 0;
        }
        printf("]\n");
        mysql_free_result(res);
    } else {
        printf("{\"error\": \"Invalid action\"}\n");
    }

    mysql_close(conn);
    return 0;
}
