# ToDo


## ORM

May want to revisit if ORM can handle SQLAlchemy binary expressions.  Some are OK, but take .where() for example.

Look at query.py _build_orm_queries when I am processing query2 wheres.  I am using split.  Cannot split on a binary expression.  Of course I could match with relation.entity.tablename == self._column(where[0], query2.tablename but there are other issues, namely that a relations name will not be the same as the columns tablename.  And for the wheres I am stripping no just the matching relations wheres but also the sub-relations under it using the relation columns string name.  So self._column() name is space_section for example, but in spaces the relation name is called just 'sections'.  I would have to do a lot of work to convert a column into a relations string.

But not sure binary expressions are important for an ORM anyhow.  For DB builder, YES, but nor for ORM.  In fact I don't even have any ORM tests written yet that use binary expressions.  Could just remove?  Revisit!
