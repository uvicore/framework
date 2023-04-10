# Hybrid

What is hybrid?  Its actually just the query builder style (non ORM) but with using actual SQLAlchemy table variables instead of strings

Example

```python
# Variable Based
post = Posts.table.c
posts = await uvicore.db.query().table(Posts.table).where(post.creator_id, 'in', [1, 2]).get()

# String based
posts = await uvicore.db.query().table('posts').where('creator_id', 'in', [1, 2]).get()
```
