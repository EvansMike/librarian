<?php
/*
 * API to get get from DB.  Part of the librarian suite of applications.
 * Sits on the http server and queries the database server requests make 
 * mobile devices.
 * Example:
 * http://saxicola.ddns.me.uk/api.librarian/book-and.php?title_search=cat
 */

/***********************************************************************
 * 
 */
function connect()
{
    try
    {
        $conn = new PDO("mysql:host=saxicola;dbname=books", "mikee", "pu5tu1e");
        $conn->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
    } 
    catch(PDOException $e) 
    {
        echo 'ERROR: ' . $e->getMessage();
        return null;
    }
    return $conn;
}

/***********************************************************************
 * 
 */
function get_books($fields)
{   
    if($fields == "") $fields = "*";
    $conn = connect();
    $stmt = $conn->prepare("SELECT $fields FROM books order by author");
    try{$stmt->execute();}
    catch(PDOException $e){ echo 'ERROR: ' . $e->getMessage(); return null;}
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}

/***********************************************************************
 * 
 */
function get_e_books()
{
    print json_encode("No e-books yet");
    return;

}
/***********************************************************************
 * 
 */
function get_borrowed_books($fields)
{ 
    if($fields == "") $fields = "title, author, name AS borrower, o_date";
    $conn = connect();
    $stmt = $conn->prepare("SELECT $fields
                FROM books, borrows, borrowers 
                WHERE books.id = borrows.book 
                AND borrows.borrower=borrowers.id 
                AND i_date is null 
                ORDER BY o_date");
    try{$stmt->execute();}
    catch(PDOException $e){ echo 'ERROR: ' . $e->getMessage(); return null;}
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    }

/***********************************************************************
 * 
 */
function get_by_title($title)
{   
    $conn = connect();
    $stmt = $conn->prepare("SELECT * FROM books 
                            WHERE title LIKE :title");
    try{ $stmt->execute(array('title' => '%'.$title.'%'));}
    catch(PDOException $e){ echo 'ERROR: ' . $e->getMessage(); return null;}
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));

}
/***********************************************************************
 * 
 */
function get_by_author($author)
{   
    $conn = connect();
    $stmt = $conn->prepare("SELECT b.title, GROUP_CONCAT(a.author_first, 
            ' ', a.author_last) AS authors, b.year FROM new_books b 
            INNER JOIN books_to_authors ba ON (b.id = ba.book_id) 
            INNER JOIN book_authors a ON (ba.author_id = a.author_id) 
            WHERE a.author_last LIKE :author 
            OR a.author_first LIKE :author
            GROUP BY b.title             
            ORDER BY author_last, author_ordinal");
    $stmt->execute(array('author' => '%'.$author.'%'));
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}

/***********************************************************************
 * Get all book title only
 */
function get_only_titles()
{
    $conn = connect();
    $stmt = $conn->prepare("SELECT title FROM new_books ORDER BY title");
    try{$stmt->execute(array('title' => '%'.$title.'%'));}
    catch(PDOException $e){ echo 'ERROR: ' . $e->getMessage(); return null;}
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}
/***********************************************************************
 * Get all book authors only
 */
function get_only_authors()
{
    $conn = connect();
    $stmt = $conn->prepare("SELECT CONCAT(author_last, ', ', author_first) AS author 
    FROM book_authors ORDER BY author_last;");
    try{$stmt->execute();}
    catch(PDOException $e){ echo 'ERROR: ' . $e->getMessage(); return null;}
    print json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
}

/***********************************************************************
 * 
 */
function return_json($stmt)
{
    $rows = array();
    while($row = $stmt->fetch()) 
    {
        $rows[] = $row;
    } 
    print json_encode($rows); 
}

/***********************************************************************
 * Authenticate user in order to add books.
 */
function authenticate()
{
    
    
}

/***********************************************************************
 * Runs from here
 */    
//$possible_url = array("get_books", "get_e_books");

if (isset($_GET["getbooks"])) get_books($_GET["getbooks"]);
if(isset($_GET["lent"])) get_borrowed_books($_GET["lent"]);
if(isset($_GET["titlesearch"])) get_by_title($_GET["titlesearch"]);
if(isset($_GET["titles"])) get_only_titles();
if(isset($_GET["getbyauthor"])) get_by_author($_GET["getbyauthor"]);
if(isset($_GET["authors"])) get_only_authors();
else connect();




?>
