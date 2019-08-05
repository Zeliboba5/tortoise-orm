from tortoise import Tortoise, fields, run_async
from tortoise.aggregation import Count, Min, Sum
from tortoise.models import Model


class Tournament(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name


class Event(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()
    tournament = fields.ForeignKeyField("models.Tournament", related_name="events")
    participants = fields.ManyToManyField(
        "models.Team", related_name="events", through="event_team"
    )

    def __str__(self):
        return self.name


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.TextField()

    def __str__(self):
        return self.name


async def run():
    await Tortoise.init(db_url="sqlite://:memory:", modules={"models": ["__main__"]})
    await Tortoise.generate_schemas()
    tournament = await Tournament.create(name="New Tournament")
    await tournament.save()
    await Tournament.create(name="Second tournament")
    await Event(name="Without participants", tournament_id=tournament.id).save()
    event = Event(name="Test", tournament_id=tournament.id)
    await event.save()
    participants = []
    for i in range(2):
        team = Team(name="Team {}".format(i + 1))
        await team.save()
        participants.append(team)
    await event.participants.add(participants[0], participants[1])
    await event.participants.add(participants[0], participants[1])

    print(await Tournament.all().annotate(events_count=Count("events")).filter(events_count__gte=1))

    print(await Event.filter(id=event.id).first().annotate(lowest_team_id=Min("participants__id")))

    print(await Tournament.all().annotate(events_count=Count("events")).order_by("events_count"))

    print(await Event.all().annotate(tournament_test_id=Sum("tournament__id")).first())


if __name__ == "__main__":
    run_async(run())
