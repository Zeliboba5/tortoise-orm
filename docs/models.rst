.. _models:

======
Models
======

Usage
=====

To get working with models, first you should import them 
 from tortoise.models import Model

With that you can start describing your own models like that

.. code-block:: python3

    class Tournament(Model):
        id = fields.IntField(pk=True)
        name = fields.TextField()
        created = fields.DatetimeField(auto_now_add=True)

        def __str__(self):
            return self.name


    class Event(Model):
        id = fields.IntField(pk=True)
        name = fields.TextField()
        tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
        participants = fields.ManyToManyField('models.Team', related_name='events', through='event_team')
        modified = fields.DatetimeField(auto_now=True)
        prize = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

        def __str__(self):
            return self.name


    class Team(Model):
        id = fields.IntField(pk=True)
        name = fields.TextField()

        def __str__(self):
            return self.name

Let see in details what we accomplished here:

.. code-block:: python3

    class Tournament(Model):

Every model should be derived from base model. You also can derive from your own model subclasses and you can make abstract models like this

.. code-block:: python3

    class AbstractTournament(Model):
        id = fields.IntField(pk=True)
        name = fields.TextField()
        created = fields.DatetimeField(auto_now_add=True)

        class Meta:
            abstract = True

        def __str__(self):
            return self.name

This models won't be created in schema generation and won't create relations to other models.

Further, let's take a look at created fields for models

.. code-block:: python3

    id = fields.IntField(pk=True)

This code defines integer primary key for table.

Currently we **only** support the primary key to be called ``id``, and to be an ``IntField``.
If you don't define a primary key, we will create a primary key of type ``IntField`` with name of ``id`` for you.

Sadly, currently only simple integer primary key is supported, there is plans to enhance this in the not too distant future.

Further we have field ``fields.DatetimeField(auto_now=True)``. Options ``auto_now`` and ``auto_now_add`` work like Django's options.

``ForeignKeyField``
-------------------

.. code-block:: python3

    tournament = fields.ForeignKeyField('models.Tournament', related_name='events')
    participants = fields.ManyToManyField('models.Team', related_name='events')
    modified = fields.DatetimeField(auto_now=True)
    prize = fields.DecimalField(max_digits=10, decimal_places=2, null=True)

In event model we got some more fields, that could be interesting for us.

``fields.ForeignKeyField('models.Tournament', related_name='events')``
    Here we create foreign key reference to tournament. We create it by referring to model by it's literal, consisting of app name and model name. `models` is default app name, but you can change it in `class Meta` with `app = 'other'`.
``related_name``
    Is keyword argument, that defines field for related query on referenced models, so with that you could fetch all tournaments's events with like this:

.. code-block:: python3

    await tournament.events.all()

or like this:

.. code-block:: python3

    await tournament.fetch_related('events')

``ManyToManyField``
-------------------

Next field is ``fields.ManyToManyField('models.Team', related_name='events')``. It describes many to many relation to model Team.



Reference
=========

.. autoclass:: tortoise.models.Model
    :members:
    :undoc-members:

