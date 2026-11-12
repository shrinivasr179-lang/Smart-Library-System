
const API_URL = "";

// SAFELY DISPLAY HTML
function escapeHTML(value) {
    return String(value ?? "").replace(/[&<>"']/g, character => ({
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#39;"
    })[character]);
}

// DISPLAY MESSAGES
function showMessage(elementId, message, success = true) {
    const element = document.getElementById(elementId);
    if (!element) return;

    element.textContent = message;
    element.style.color = success ? "green" : "red";
}


// CHECK LOGIN SESSION
async function checkAdminSession() {
    try {
        const response = await fetch(`${API_URL}/api/session`, {
            credentials: "same-origin"
        });

        if (!response.ok) {
            window.location.href = "/login";
            return false;
        }

        const result = await response.json();

        if (!result.logged_in) {
            window.location.href = "/login";
            return false;
        }

        const name = result.name || "Admin";
        const nameElement = document.getElementById("adminName");
        const avatarElement = document.getElementById("adminAvatar");

        if (nameElement) nameElement.textContent = name;

        if (avatarElement) {
            avatarElement.textContent = name.charAt(0).toUpperCase();
        }

        return true;

    } catch (error) {
        console.error("Session check failed:", error);
        window.location.href = "/login";
        return false;
    }
}


// ADMIN LOGOUT
async function logoutAdmin() {
    const confirmed = confirm("Are you sure you want to logout?");

    if (!confirmed) return;

    try {
        const response = await fetch(`${API_URL}/api/logout`, {
            method: "POST",
            credentials: "same-origin"
        });

        const result = await response.json();

        if (!response.ok || !result.success) {
            throw new Error(result.message || "Logout failed");
        }

        window.location.href = "/login";

    } catch (error) {
        alert(error.message);
    }
}


// LOAD STUDENTS
async function loadStudents() {
    try {
        const response = await fetch(`${API_URL}/api/students`);

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) throw new Error("Unable to load students");

        const students = await response.json();

        document.getElementById("studentCount").textContent =
            students.length;

        let html = `
            <table>
                <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Email</th>
                    <th>Department</th>
                </tr>
        `;

        students.forEach(student => {
            html += `
                <tr>
                    <td>${escapeHTML(student.student_id)}</td>
                    <td>${escapeHTML(student.name)}</td>
                    <td>${escapeHTML(student.email)}</td>
                    <td>${escapeHTML(student.department)}</td>
                </tr>
            `;
        });

        html += "</table>";

        document.getElementById("studentsContainer").innerHTML = html;

        const select = document.getElementById("issueStudent");

        select.innerHTML = '<option value="">Select Student</option>';

        students.forEach(student => {
            select.innerHTML += `
                <option value="${escapeHTML(student.student_id)}">
                    ${escapeHTML(student.name)}
                </option>
            `;
        });

    } catch (error) {
        document.getElementById("studentsContainer").textContent =
            "Unable to load students. Check Flask server.";

        console.error(error);
    }
}


// LOAD BOOKS
async function loadBooks() {
    try {
        const response = await fetch(`${API_URL}/api/books`);

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) throw new Error("Unable to load books");

        const books = await response.json();

        document.getElementById("bookCount").textContent =
            books.length;

        displayBooks(books, "booksContainer");

        const select = document.getElementById("issueBook");

        select.innerHTML = '<option value="">Select Book</option>';

        books.filter(book => Number(book.available_copies) > 0)
            .forEach(book => {
                select.innerHTML += `
                    <option value="${escapeHTML(book.book_id)}">
                        ${escapeHTML(book.title)}
                        (${escapeHTML(book.available_copies)} available)
                    </option>
                `;
            });

    } catch (error) {
        document.getElementById("booksContainer").textContent =
            "Unable to load books. Check Flask server.";

        console.error(error);
    }
}


// DISPLAY BOOKS
function displayBooks(books, containerId) {
    let html = `
        <table>
            <tr>
                <th>Book ID</th>
                <th>Title</th>
                <th>Author</th>
                <th>Category</th>
                <th>Total Copies</th>
                <th>Available</th>
            </tr>
    `;

    if (books.length === 0) {
        html += `<tr><td colspan="6">No books found.</td></tr>`;
    }

    books.forEach(book => {
        html += `
            <tr>
                <td>${escapeHTML(book.book_id)}</td>
                <td>${escapeHTML(book.title)}</td>
                <td>${escapeHTML(book.author)}</td>
                <td>${escapeHTML(book.category_name || "Uncategorized")}</td>
                <td>${escapeHTML(book.total_copies)}</td>
                <td>${escapeHTML(book.available_copies)}</td>
            </tr>
        `;
    });

    html += "</table>";

    const container = document.getElementById(containerId);

    if (container) {
        container.innerHTML = html;
    }
}


// LOAD CATEGORIES
async function loadCategories() {
    const categorySelect = document.getElementById("bookCategory");

    if (!categorySelect) return;

    try {
        const response = await fetch(`${API_URL}/api/categories`);

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) throw new Error("Unable to load categories");

        const categories = await response.json();

        categorySelect.innerHTML =
            '<option value="">Select category</option>';

        categories.forEach(category => {
            categorySelect.innerHTML += `
                <option value="${escapeHTML(category.category_id)}">
                    ${escapeHTML(category.category_name)}
                </option>
            `;
        });

        if (categories.length === 0) {
            showMessage("bookMessage", "No categories found.", false);
        }

    } catch (error) {
        showMessage("bookMessage", error.message, false);
        console.error(error);
    }
}


// ADD STUDENT
async function addStudent(event) {
    event.preventDefault();

    const student = {
        name: document.getElementById("studentName").value.trim(),
        email: document.getElementById("studentEmail").value.trim(),
        department: document.getElementById("studentDepartment").value.trim()
    };

    try {
        const response = await fetch(`${API_URL}/api/students`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(student)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || result.message);
        }

        showMessage("studentMessage", "Student added successfully!");

        document.getElementById("studentForm").reset();

        await loadStudents();
        await loadDashboardCharts();

    } catch (error) {
        showMessage("studentMessage", error.message, false);
    }
}


// ADD BOOK
async function addBook(event) {
    event.preventDefault();

    const book = {
        title: document.getElementById("bookTitle").value.trim(),
        author: document.getElementById("bookAuthor").value.trim(),
        category_id: document.getElementById("bookCategory").value,
        total_copies: document.getElementById("bookCopies").value
    };

    try {
        const response = await fetch(`${API_URL}/api/books`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify(book)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || result.message);
        }

        showMessage("bookMessage", "Book added successfully!");

        document.getElementById("bookForm").reset();

        await Promise.all([
            loadBooks(),
            loadDashboardCharts(),
            loadLowStockBooks()
        ]);

    } catch (error) {
        showMessage("bookMessage", error.message, false);
    }
}


// SEARCH BOOKS
async function searchBooks() {
    const search = document.getElementById("searchInput").value.trim();

    if (!search) {
        alert("Please enter a book title.");
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/books/search?q=${encodeURIComponent(search)}`
        );

        const books = await response.json();

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            throw new Error(books.error || "Search failed");
        }

        displayBooks(books, "searchResults");

    } catch (error) {
        alert(error.message);
    }
}


// SHOW ALL BOOKS
function showAllBooks() {
    document.getElementById("searchInput").value = "";
    document.getElementById("searchResults").innerHTML = "";

    loadBooks();
}


// ISSUE BOOK
async function issueBook(event) {
    event.preventDefault();

    const studentId = document.getElementById("issueStudent").value;
    const bookId = document.getElementById("issueBook").value;

    if (!studentId || !bookId) {
        showMessage("issueMessage", "Select a student and book.", false);
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/issue`, {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                student_id: studentId,
                book_id: bookId
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || result.message);
        }

        showMessage(
            "issueMessage",
            `Book issued successfully! Due date: ${result.due_date}`
        );

        document.getElementById("issueForm").reset();

        await Promise.all([
            loadBooks(),
            loadIssues(),
            loadDashboardCharts(),
            loadOverdueBooks(),
            loadLowStockBooks(),
            loadReservations()
        ]);

    } catch (error) {
        showMessage("issueMessage", error.message, false);
    }
}


// LOAD ISSUE RECORDS
async function loadIssues() {
    try {
        const response = await fetch(`${API_URL}/api/issues`);

        if (response.status === 401) {
            window.location.href = "/login";
            return;
        }

        if (!response.ok) {
            throw new Error("Unable to load issue records");
        }

        const issues = await response.json();

        let html = `
            <table>
                <tr>
                    <th>Issue ID</th>
                    <th>Student</th>
                    <th>Book</th>
                    <th>Issue Date</th>
                    <th>Due Date</th>
                    <th>Return Date</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
        `;

        if (issues.length === 0) {
            html += `
                <tr>
                    <td colspan="8">No issue records found.</td>
                </tr>
            `;
        }

        issues.forEach(issue => {
            const isIssued = issue.status === "Issued";

            html += `
                <tr>
                    <td>${escapeHTML(issue.issue_id)}</td>
                    <td>${escapeHTML(issue.student_name)}</td>
                    <td>${escapeHTML(issue.book_title)}</td>
                    <td>${escapeHTML(issue.issue_date)}</td>
                    <td>${escapeHTML(issue.due_date)}</td>
                    <td>${escapeHTML(issue.return_date || "-")}</td>
                    <td>${escapeHTML(issue.status)}</td>
                    <td>
                        ${isIssued
                            ? `<button type="button"
                                onclick="returnBook(${Number(issue.issue_id)})">
                                Return
                               </button>`
                            : "Completed"}
                    </td>
                </tr>
            `;
        });

        html += "</table>";

        document.getElementById("issuesContainer").innerHTML = html;

    } catch (error) {
        document.getElementById("issuesContainer").textContent =
            "Unable to load issue records.";

        console.error(error);
    }
}


// RETURN BOOK
async function returnBook(issueId) {
    if (!confirm("Are you sure you want to return this book?")) {
        return;
    }

    try {
        const response = await fetch(
            `${API_URL}/api/return/${issueId}`,
            {method: "POST"}
        );

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || result.message);
        }

        alert("Book returned successfully!");

        await Promise.all([
            loadBooks(),
            loadIssues(),
            loadDashboardCharts(),
            loadOverdueBooks(),
            loadLowStockBooks(),
            loadReservations()
        ]);

    } catch (error) {
        alert(error.message);
    }
}


// ======================================
// DASHBOARD CHARTS
// ======================================

let categoryChartInstance = null;
let libraryChartInstance = null;


async function loadDashboardCharts() {
    try {
        const response = await fetch(
            `${API_URL}/api/dashboard-stats`,
            { credentials: "same-origin" }
        );

        if (!response.ok) {
            throw new Error("Unable to load dashboard statistics");
        }

        const data = await response.json();

        const studentCount = document.getElementById("studentCount");
        const bookCount = document.getElementById("bookCount");

        if (studentCount) {
            studentCount.textContent = data.total_students;
        }

        if (bookCount) {
            bookCount.textContent = data.total_books;
        }

        // BOOKS BY CATEGORY CHART
        const categoryCanvas = document.getElementById("categoryChart");

        if (categoryCanvas) {
            if (categoryChartInstance) {
                categoryChartInstance.destroy();
            }

            categoryChartInstance = new Chart(categoryCanvas, {
                type: "doughnut",
                data: {
                    labels: data.categories.map(
                        item => item.category_name
                    ),
                    datasets: [{
                        label: "Books",
                        data: data.categories.map(
                            item => item.total_books
                        ),
                        backgroundColor: [
                            "#2563eb",
                            "#16a34a",
                            "#f59e0b",
                            "#9333ea",
                            "#ef4444",
                            "#0891b2",
                            "#db2777"
                        ],
                        borderWidth: 2,
                        borderColor: "#ffffff"
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    plugins: {
                        legend: {
                            position: "bottom"
                        }
                    }
                }
            });
        }

        // LIBRARY OVERVIEW CHART
        const libraryCanvas = document.getElementById("libraryChart");

        if (libraryCanvas) {
            if (libraryChartInstance) {
                libraryChartInstance.destroy();
            }

            libraryChartInstance = new Chart(libraryCanvas, {
                type: "bar",
                data: {
                    labels: [
                        "Available Books",
                        "Issued Books",
                        "Returned Books"
                    ],
                    datasets: [{
                        label: "Number of Books",
                        data: [
                            data.available_books,
                            data.issued_books,
                            data.returned_books
                        ],
                        backgroundColor: [
                            "#16a34a",
                            "#2563eb",
                            "#f59e0b"
                        ],
                        borderRadius: 7
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: true,
                    scales: {
                        y: {
                            beginAtZero: true,
                            ticks: {
                                precision: 0
                            }
                        }
                    },
                    plugins: {
                        legend: {
                            display: false
                        }
                    }
                }
            });
        }

    } catch (error) {
        console.error("Dashboard charts error:", error);
    }
}


// ======================================
// OVERDUE BOOKS ALERT
// ======================================

async function loadOverdueBooks() {
    const container = document.getElementById("overdueBooksContainer");

    if (!container) return;

    try {
        const response = await fetch(
            `${API_URL}/api/overdue-books`,
            { credentials: "same-origin" }
        );

        if (!response.ok) {
            throw new Error("Unable to load overdue books");
        }

        const data = await response.json();

        if (data.overdue_books.length === 0) {
            container.innerHTML = `
                <p style="color: green;">
                    ✓ No overdue books. All books are on time!
                </p>
            `;
            return;
        }

        container.innerHTML = `
            <p style="color: #dc3545; font-weight: bold;">
                ${data.total_overdue} overdue book(s) found
            </p>

            <table>
                <thead>
                    <tr>
                        <th>Student</th>
                        <th>Book</th>
                        <th>Due Date</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.overdue_books.map(book => `
                        <tr>
                            <td>${escapeHTML(book.student_name)}</td>
                            <td>${escapeHTML(book.book_title)}</td>
                            <td>${escapeHTML(book.due_date)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;

    } catch (error) {
        container.innerHTML = `
            <p style="color: red;">
                Unable to load overdue books.
            </p>
        `;
        console.error("Overdue books error:", error);
    }
}


// ======================================
// LOW STOCK WARNING
// ======================================

async function loadLowStockBooks() {
    const container = document.getElementById("lowStockBooksContainer");

    if (!container) return;

    try {
        const response = await fetch(
            `${API_URL}/api/low-stock-books`,
            { credentials: "same-origin" }
        );

        if (!response.ok) {
            throw new Error("Unable to load low stock books");
        }

        const data = await response.json();

        if (data.low_stock_books.length === 0) {
            container.innerHTML = `
                <p style="color: green;">
                    ✓ No low stock books. Stock levels are healthy!
                </p>
            `;
            return;
        }

        container.innerHTML = `
            <p style="color: #e69500; font-weight: bold;">
                ${data.total_low_stock} low stock book(s) found
            </p>

            <table>
                <thead>
                    <tr>
                        <th>Book ID</th>
                        <th>Book Title</th>
                        <th>Total Copies</th>
                        <th>Available Copies</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.low_stock_books.map(book => `
                        <tr>
                            <td>${escapeHTML(book.book_id)}</td>
                            <td>${escapeHTML(book.title)}</td>
                            <td>${escapeHTML(book.total_copies)}</td>
                            <td>${escapeHTML(book.available_copies)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;

    } catch (error) {
        container.innerHTML = `
            <p style="color: red;">
                Unable to load low stock books.
            </p>
        `;
        console.error("Low stock books error:", error);
    }
}


// =====================================
// BOOK RESERVATION SYSTEM
// =====================================


// LOAD RESERVATION RECORDS
async function loadReservations() {
    const container = document.getElementById("reservationsContainer");

    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/api/reservations`, {
            credentials: "same-origin"
        });

        if (!response.ok) {
            throw new Error("Unable to load reservations");
        }

        const data = await response.json();

        if (data.reservations.length === 0) {
            container.innerHTML = "<p>No reservations found.</p>";
            return;
        }

        let html = `
            <table>
                <thead>
                    <tr>
                        <th>Reservation ID</th>
                        <th>Student Name</th>
                        <th>Book Title</th>
                        <th>Reservation Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
        `;

        data.reservations.forEach(reservation => {
            const id = Number(reservation.reservation_id);

            html += `
                <tr>
                    <td>${escapeHTML(id)}</td>
                    <td>${escapeHTML(reservation.student_name)}</td>
                    <td>${escapeHTML(reservation.book_title)}</td>
                    <td>${escapeHTML(reservation.reservation_date)}</td>

                    <td>
                        <select id="reservationStatus-${id}">
                            <option value="Pending"
                                ${reservation.status === "Pending" ? "selected" : ""}>
                                Pending
                            </option>

                            <option value="Ready"
                                ${reservation.status === "Ready" ? "selected" : ""}>
                                Ready
                            </option>

                            <option value="Completed"
                                ${reservation.status === "Completed" ? "selected" : ""}>
                                Completed
                            </option>

                            <option value="Cancelled"
                                ${reservation.status === "Cancelled" ? "selected" : ""}>
                                Cancelled
                            </option>
                        </select>

                        <button
                            type="button"
                            onclick="updateReservationStatus(${id})">
                            Update
                        </button>
                    </td>
                </tr>
            `;
        });

        html += "</tbody></table>";

        container.innerHTML = html;

    } catch (error) {
        container.innerHTML = `
            <p style="color:red;">
                Unable to load reservations.
            </p>
        `;
        console.error(error);
    }
}


// ADD NEW RESERVATION
async function addReservation(event) {
    event.preventDefault();

    const studentId =
        document.getElementById("reservationStudentId").value;

    const bookId =
        document.getElementById("reservationBookId").value;

    const message =
        document.getElementById("reservationMessage");

    try {
        const response = await fetch(`${API_URL}/api/reservations`, {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                student_id: studentId,
                book_id: bookId
            })
        });

        const data = await response.json();

        if (!response.ok) {
            message.style.color = "red";
            message.textContent = data.error || "Reservation failed.";
            return;
        }

        message.style.color = "green";
        message.textContent = data.message;

        document.getElementById("reservationForm").reset();

        await loadReservations();

    } catch (error) {
        message.style.color = "red";
        message.textContent = "Unable to connect to the server.";
        console.error(error);
    }
}


// UPDATE RESERVATION STATUS
async function updateReservationStatus(reservationId) {
    const statusSelect = document.getElementById(
        `reservationStatus-${reservationId}`
    );

    if (!statusSelect) return;

    const newStatus = statusSelect.value;

    try {
        const response = await fetch(
            `${API_URL}/api/reservations/${reservationId}`,
            {
                method: "PUT",
                credentials: "same-origin",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    status: newStatus
                })
            }
        );

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Status update failed.");
        }

        const message = document.getElementById("reservationMessage");

        if (message) {
            message.style.color = "green";
            message.textContent = data.message;
        }

        await loadReservations();

    } catch (error) {
        const message = document.getElementById("reservationMessage");

        if (message) {
            message.style.color = "red";
            message.textContent = error.message;
        }

        console.error("Reservation update error:", error);
    }
}


// =====================================
// START WEBSITE
// =====================================

document.addEventListener("DOMContentLoaded", async () => {

    const loggedIn = await checkAdminSession();

    if (!loggedIn) return;

    await Promise.all([
        loadStudents(),
        loadBooks(),
        loadCategories(),
        loadIssues(),
        loadDashboardCharts(),
        loadOverdueBooks(),
        loadLowStockBooks(),
        loadReservations()
    ]);

    const studentForm = document.getElementById("studentForm");

    if (studentForm) {
        studentForm.addEventListener("submit", addStudent);
    }

    const bookForm = document.getElementById("bookForm");

    if (bookForm) {
        bookForm.addEventListener("submit", addBook);
    }

    const issueForm = document.getElementById("issueForm");

    if (issueForm) {
        issueForm.addEventListener("submit", issueBook);
    }

    const reservationForm = document.getElementById("reservationForm");

    if (reservationForm) {
        reservationForm.addEventListener("submit", addReservation);
    }

});

// ==========================================
// STUDENT ATTENDANCE JAVASCRIPT
// ==========================================

// Set today's date automatically
const attendanceDateInput = document.getElementById("attendanceDate");

if (attendanceDateInput) {
    attendanceDateInput.value = new Date().toISOString().split("T")[0];

    attendanceDateInput.addEventListener("change", loadAttendance);
}


// Load students into attendance dropdown
async function loadAttendanceStudents() {
    try {
        const response = await fetch(`${API_URL}/api/students`);
        const students = await response.json();

        const select = document.getElementById("attendanceStudent");

        if (!select) return;

        select.innerHTML = '<option value="">Select Student</option>';

        students.forEach(student => {
            const option = document.createElement("option");
            option.value = student.student_id;
            option.textContent = `${student.name} (ID: ${student.student_id})`;
            select.appendChild(option);
        });

    } catch (error) {
        console.error("Attendance students error:", error);
    }
}


// Save student attendance
async function saveAttendance() {
    const studentId = document.getElementById("attendanceStudent").value;
    const attendanceDate = document.getElementById("attendanceDate").value;
    const status = document.getElementById("attendanceStatus").value;
    const remarks = document.getElementById("attendanceRemarks").value;

    const message = document.getElementById("attendanceMessage");

    if (!studentId || !attendanceDate) {
        message.textContent = "Please select a student and date.";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/attendance`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                student_id: studentId,
                attendance_date: attendanceDate,
                status: status,
                remarks: remarks
            })
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to save attendance.");
        }

        message.textContent = result.message;
        message.style.color = "green";

        document.getElementById("attendanceRemarks").value = "";

        await loadAttendance();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}


// Display attendance records
async function loadAttendance() {
    const date = document.getElementById("attendanceDate").value;
    const table = document.getElementById("attendanceTable");

    if (!date || !table) return;

    try {
        const response = await fetch(
            `${API_URL}/api/attendance?date=${encodeURIComponent(date)}`
        );

        const records = await response.json();

        if (!response.ok) {
            throw new Error(records.error || "Unable to load attendance.");
        }

        if (records.length === 0) {
            table.innerHTML = `
                <tr>
                    <td colspan="5">No attendance records found.</td>
                </tr>
            `;
            return;
        }

        table.innerHTML = records.map(record => `
            <tr>
                <td>${escapeHTML(record.student_id)}</td>
                <td>${escapeHTML(record.student_name)}</td>
                <td>${escapeHTML(record.department)}</td>
                <td>${escapeHTML(record.status)}</td>
                <td>${escapeHTML(record.remarks || "-")}</td>
            </tr>
        `).join("");

    } catch (error) {
        console.error("Attendance loading error:", error);
        table.innerHTML = `
            <tr>
                <td colspan="5">Unable to load attendance.</td>
            </tr>
        `;
    }
}


// ==========================================
// LIBRARY CALENDAR JAVASCRIPT
// ==========================================


// Add new library event
async function addLibraryEvent(event) {
    event.preventDefault();

    const message = document.getElementById("eventMessage");

    const eventData = {
        event_title: document.getElementById("eventTitle").value.trim(),
        description: document.getElementById("eventDescription").value.trim(),
        event_date: document.getElementById("eventDate").value,
        event_type: document.getElementById("eventType").value
    };

    if (!eventData.event_title || !eventData.event_date) {
        message.textContent = "Please enter event title and date.";
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/events`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(eventData)
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to add event.");
        }

        message.textContent = result.message;
        message.style.color = "green";

        document.getElementById("eventForm").reset();

        await loadCalendarEvents();

    } catch (error) {
        message.textContent = error.message;
        message.style.color = "red";
    }
}


// Load calendar events
async function loadCalendarEvents() {
    const container = document.getElementById("calendarEvents");

    if (!container) return;

    try {
        const response = await fetch(`${API_URL}/api/events`);
        const events = await response.json();

        if (!response.ok) {
            throw new Error("Unable to load events.");
        }

        if (events.length === 0) {
            container.innerHTML = "<p>No library events available.</p>";
            return;
        }

        container.innerHTML = events.map(event => `
            <div class="event-card">
                <h3>${escapeHTML(event.event_title)}</h3>
                <p>${escapeHTML(event.description || "No description")}</p>
                <p><strong>Date:</strong> ${escapeHTML(event.event_date)}</p>
                <p><strong>Type:</strong> ${escapeHTML(event.event_type)}</p>

                <button
                    type="button"
                    onclick="deleteLibraryEvent(${Number(event.event_id)})">
                    Delete Event
                </button>
            </div>
        `).join("");

    } catch (error) {
        console.error("Calendar loading error:", error);
        container.innerHTML = "<p>Unable to load library events.</p>";
    }
}


// Delete library event
async function deleteLibraryEvent(eventId) {
    if (!confirm("Are you sure you want to delete this event?")) {
        return;
    }

    try {
        const response = await fetch(`${API_URL}/api/events/${eventId}`, {
            method: "DELETE"
        });

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || "Unable to delete event.");
        }

        alert(result.message);

        await loadCalendarEvents();

    } catch (error) {
        alert(error.message);
    }
}


// ==========================================
// INITIALIZE ATTENDANCE AND CALENDAR
// ==========================================

const eventForm = document.getElementById("eventForm");

if (eventForm) {
    eventForm.addEventListener("submit", addLibraryEvent);
}

loadAttendanceStudents();
loadAttendance();
loadCalendarEvents();
