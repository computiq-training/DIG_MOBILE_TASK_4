## Task 4

Implement the following routes:

`POST` `/movies/favorites/{id}`
`DELETE` `/movies/favorites/{id}`

`POST` `/series/favorites/{id}`
`DELETE` `/series/favorites/{id}`

Where each `POST` request will add that particular (movie or serial) to the user favorites list (of movies or series)
AND each `DELETE` request will remove that from their favorite list.

----
----

#### BONUS TASK

Implement Pagination for the routes that are listing movies or series.

`Hint: ` You can look for the class `Paginator` that django provides and take advantage of it.

Best of Luck ✌🏻