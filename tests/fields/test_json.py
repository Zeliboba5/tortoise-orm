from tests import testmodels
from tortoise.contrib import test
from tortoise.exceptions import ConfigurationError, FieldError, IntegrityError
from tortoise.fields import JSONField


class TestJSONFields(test.TestCase):
    async def test_empty(self):
        with self.assertRaises(IntegrityError):
            await testmodels.JSONFields.create()

    async def test_create(self):
        obj0 = await testmodels.JSONFields.create(data={"some": ["text", 3]})
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data, {"some": ["text", 3]})
        self.assertEqual(obj.data_null, None)
        await obj.save()
        obj2 = await testmodels.JSONFields.get(id=obj.id)
        self.assertEqual(obj, obj2)

    async def test_error(self):
        with self.assertRaises(FieldError):
            await testmodels.JSONFields.create(data='{"some": ')

        obj = await testmodels.JSONFields.create(data='{"some": ["text", 3]}')
        with self.assertRaises(FieldError):
            await testmodels.JSONFields.filter(pk=obj.pk).update(data='{"some": ')

        with self.assertRaises(FieldError):
            obj.data = "error json"
            await obj.save()

    async def test_update(self):
        obj0 = await testmodels.JSONFields.create(data={"some": ["text", 3]})
        await testmodels.JSONFields.filter(id=obj0.id).update(data={"other": ["text", 5]})
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data, {"other": ["text", 5]})
        self.assertEqual(obj.data_null, None)

    async def test_dict_str(self):
        obj0 = await testmodels.JSONFields.create(data={"some": ["text", 3]})

        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data, {"some": ["text", 3]})

        await testmodels.JSONFields.filter(id=obj0.id).update(data='{"other": ["text", 5]}')
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data, {"other": ["text", 5]})

    async def test_list_str(self):
        obj = await testmodels.JSONFields.create(data='["text", 3]')
        obj0 = await testmodels.JSONFields.get(id=obj.id)
        self.assertEqual(obj0.data, ["text", 3])

        await testmodels.JSONFields.filter(id=obj.id).update(data='["text", 5]')
        obj0 = await testmodels.JSONFields.get(id=obj.id)
        self.assertEqual(obj0.data, ["text", 5])

    async def test_list(self):
        obj0 = await testmodels.JSONFields.create(data=["text", 3])
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data, ["text", 3])
        self.assertEqual(obj.data_null, None)
        await obj.save()
        obj2 = await testmodels.JSONFields.get(id=obj.id)
        self.assertEqual(obj, obj2)

    async def test_list_contains(self):
        await testmodels.JSONFields.create(data=["text", 3, {"msg": "msg2"}])
        obj = await testmodels.JSONFields.filter(data__contains=[{"msg": "msg2"}]).first()
        self.assertEqual(obj.data, ["text", 3, {"msg": "msg2"}])
        await obj.save()
        obj2 = await testmodels.JSONFields.get(id=obj.id)
        self.assertEqual(obj, obj2)

    async def test_list_contained_by(self):
        obj0 = await testmodels.JSONFields.create(data=["text"])
        obj1 = await testmodels.JSONFields.create(data=["tortoise", "msg"])
        obj2 = await testmodels.JSONFields.create(data=["tortoise"])
        objs = set(
            await testmodels.JSONFields.filter(data__contained_by=["text", "tortoise", "msg"])
        )
        created_objs = {obj0, obj1, obj2}
        self.assertSetEqual(created_objs, objs)

    async def test_filter(self):
        obj0 = await testmodels.JSONFields.create(
            data={
                "breed": "labrador",
                "owner": {
                    "name": "Bob",
                    "last": None,
                    "other_pets": [
                        {
                            "name": "Fishy",
                        }
                    ],
                },
            }
        )
        obj = await testmodels.JSONFields.filter(data__filter={"breed": "labrador"}).first()
        self.assertEqual(obj0, obj)
        obj2 = await testmodels.JSONFields.filter(data__filter={"owner__name": "Bob"}).first()
        self.assertEqual(obj0, obj2)
        obj3 = await testmodels.JSONFields.filter(
            data__filter={"owner__other_pets__0__name": "Fishy"}
        ).first()
        self.assertEqual(obj0, obj3)

    async def test_filter_not_condition(self):
        obj0 = await testmodels.JSONFields.create(
            data={
                "breed": "labrador",
                "owner": {
                    "name": "Bob",
                    "last": None,
                    "other_pets": [
                        {
                            "name": "Fishy",
                        }
                    ],
                },
            }
        )

        obj1 = await testmodels.JSONFields.filter(data__filter={"breed__not": "a"}).first()
        self.assertEqual(obj0, obj1)

    async def test_filter_is_null_condition(self):
        obj0 = await testmodels.JSONFields.create(
            data={
                "breed": "labrador",
                "owner": {
                    "name": None,
                    "last": "Cloud",
                    "other_pets": [
                        {
                            "name": "Fishy",
                        }
                    ],
                },
            }
        )

        obj1 = await testmodels.JSONFields.filter(
            data__filter={"owner__name__isnull": True}
        ).first()

        self.assertEqual(obj0, obj1)

    async def test_filter_not_is_null_condition(self):
        obj0 = await testmodels.JSONFields.create(
            data={
                "breed": "labrador",
                "owner": {
                    "name": "Boby",
                    "last": None,
                    "other_pets": [
                        {
                            "name": "Fishy",
                        }
                    ],
                },
            }
        )

        obj1 = await testmodels.JSONFields.filter(
            data__filter={"owner__last__not_isnull": False}
        ).first()
        self.assertEqual(obj0, obj1)

    async def test_values(self):
        obj0 = await testmodels.JSONFields.create(data={"some": ["text", 3]})
        values = await testmodels.JSONFields.filter(id=obj0.id).values("data")
        self.assertEqual(values[0]["data"], {"some": ["text", 3]})

    async def test_values_list(self):
        obj0 = await testmodels.JSONFields.create(data={"some": ["text", 3]})
        values = await testmodels.JSONFields.filter(id=obj0.id).values_list("data", flat=True)
        self.assertEqual(values[0], {"some": ["text", 3]})

    def test_unique_fail(self):
        with self.assertRaisesRegex(ConfigurationError, "can't be indexed"):
            JSONField(unique=True)

    def test_index_fail(self):
        with self.assertRaisesRegex(ConfigurationError, "can't be indexed"):
            JSONField(index=True)

    async def test_validate_str(self):
        obj0 = await testmodels.JSONFields.create(data=[], data_validate='["text", 5]')
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data_validate, ["text", 5])

    async def test_validate_dict(self):
        obj0 = await testmodels.JSONFields.create(data=[], data_validate={"some": ["text", 3]})
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data_validate, {"some": ["text", 3]})

    async def test_validate_list(self):
        obj0 = await testmodels.JSONFields.create(data=[], data_validate=["text", 3])
        obj = await testmodels.JSONFields.get(id=obj0.id)
        self.assertEqual(obj.data_validate, ["text", 3])
