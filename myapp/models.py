# This is an auto-generated Django model module.

# You'll have to do the following manually to clean this up:

#   * Rearrange models' order

#   * Make sure each model has one field with primary_key=True

#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior

#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table

# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models


class Drivers(models.Model):
    id = models.UUIDField(primary_key=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False

        db_table = "drivers"


class Leagues(models.Model):
    id = models.UUIDField(primary_key=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False

        db_table = "leagues"


class LeaguesDrivers(models.Model):
    id = models.UUIDField(primary_key=True)

    is_reserve = models.BooleanField(blank=True, null=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING)

    league = models.ForeignKey(Leagues, models.DO_NOTHING)

    team = models.ForeignKey("Teams", models.DO_NOTHING)

    class Meta:
        managed = False

        db_table = "leagues_drivers"


class Races(models.Model):
    id = models.UUIDField(primary_key=True)

    date = models.DateTimeField()

    name = models.TextField()

    track = models.ForeignKey("Tracks", models.DO_NOTHING)

    league = models.ForeignKey(Leagues, models.DO_NOTHING)

    class Meta:
        managed = False

        db_table = "races"


class RacesDrivers(models.Model):
    id = models.UUIDField(primary_key=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING)

    race = models.ForeignKey(Races, models.DO_NOTHING)

    team = models.ForeignKey("Teams", models.DO_NOTHING)

    class Meta:
        managed = False

        db_table = "races_drivers"


class Roles(models.Model):
    id = models.UUIDField(primary_key=True)

    name = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False

        db_table = "roles"


class Teams(models.Model):
    id = models.UUIDField(primary_key=True)

    name = models.CharField(unique=True, max_length=100)

    icon = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False

        db_table = "teams"


class Tokens(models.Model):
    id = models.UUIDField(primary_key=True)

    user = models.ForeignKey("Users", models.DO_NOTHING)

    token = models.TextField(unique=True)

    class Meta:
        managed = False

        db_table = "tokens"


class Tracks(models.Model):
    id = models.UUIDField(primary_key=True)

    name = models.CharField(max_length=50)

    flag = models.BinaryField(blank=True, null=True)

    class Meta:
        managed = False

        db_table = "tracks"


class Users(models.Model):
    id = models.UUIDField(primary_key=True)

    login = models.CharField(unique=True, max_length=50)

    password = models.BinaryField()

    class Meta:
        managed = False

        db_table = "users"


class UsersRoles(models.Model):
    id = models.UUIDField(primary_key=True)

    user = models.ForeignKey(Users, models.DO_NOTHING)

    role_id = models.UUIDField()

    class Meta:
        managed = False

        db_table = "users_roles"
