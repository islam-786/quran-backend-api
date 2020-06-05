from fireo.models import Model
from fireo.fields import IDField, TextField, NumberField


class Ayah(Model):
    id = IDField()
    surah_id = TextField()
    number = NumberField(int_only=True)
    number_in_surah = NumberField(int_only=True)
    arabic = TextField()

    class Meta:
        collection_name = "quran_ayahs"