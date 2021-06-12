import os
from sqlalchemy import Column, String, Integer
from flask_sqlalchemy import SQLAlchemy
import json

database_filename = "database.db"
project_dir = os.path.dirname(os.path.abspath(__file__))
database_path = "sqlite:///{}".format(
    os.path.join(project_dir, database_filename))

db = SQLAlchemy()


def setup_db(app):
    ''' binds a flask application and a SQLAlchemy service '''

    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)


def db_drop_and_create_all():
    '''
        drops the database tables and starts fresh
        can be used to initialize a clean database
        !!NOTE you can change the database_filename variable to have multiple versions of a database
    '''

    db.drop_all()
    db.create_all()
    # add one demo row which is helping in POSTMAN test
    drink = Drink(
        title='water',
        recipe='[{"name": "water", "color": "blue", "parts": 1}]'
    )


class Drink(db.Model):
    ''' Drink
        a persistent drink entity, extends the base SQLAlchemy Model
    '''

    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), unique=True)
    # the ingredients blob - this stores a lazy json blob
    # the required datatype is [{'color': string, 'name':string,
    # 'parts':number}]
    recipe = Column(String(180), nullable=False)

    def short(self):
        ''' short form representation of the Drink model '''

        print(json.loads(self.recipe))
        short_recipe = [{'color': r['color'], 'parts': r['parts']}
                        for r in json.loads(self.recipe)]
        return {
            'id': self.id,
            'title': self.title,
            'recipe': short_recipe
        }

    def long(self):
        ''' long form representation of the Drink model '''

        return {
            'id': self.id,
            'title': self.title,
            'recipe': json.loads(self.recipe)
        }

    def insert(self):
        '''
            inserts a new model into a database
            the model must have a unique name
            the model must have a unique id or null id
            EXAMPLE
                drink = Drink(title=req_title, recipe=req_recipe)
                drink.insert()
        '''

        db.session.add(self)
        db.session.commit()

    def delete(self):
        '''
            deletes a new model into a database
            the model must exist in the database
            EXAMPLE
                drink = Drink(title=req_title, recipe=req_recipe)
                drink.delete()
        '''

        db.session.delete(self)
        db.session.commit()

    def update(self):
        '''
            updates a new model into a database
            the model must exist in the database
            EXAMPLE
                drink = Drink.query.filter(Drink.id == id).one_or_none()
                drink.title = 'Black Coffee'
                drink.update()
        '''

        db.session.commit()

    def __repr__(self):
        return json.dumps(self.short())
