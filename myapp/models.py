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

    name = models.CharField(unique=True, max_length=50, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'drivers'





class Penalties(models.Model):

    id = models.UUIDField(primary_key=True)

    time = models.IntegerField(blank=True, null=True)

    penalty_points = models.IntegerField(blank=True, null=True)

    issued_at = models.DateTimeField(blank=True, null=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING)

    report = models.ForeignKey('Reports', models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'penalties'

        unique_together = (('driver', 'report'),)





class Races(models.Model):

    id = models.UUIDField(primary_key=True)

    date = models.DateTimeField()

    is_sprint = models.BooleanField(blank=True, null=True)

    track = models.ForeignKey('Tracks', models.DO_NOTHING)

    season = models.ForeignKey('Seasons', models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'races'

        unique_together = (('season', 'date', 'is_sprint'),)





class RacesDrivers(models.Model):

    id = models.UUIDField(primary_key=True)

    time = models.FloatField(blank=True, null=True)

    has_fastest_lap = models.BooleanField(blank=True, null=True)

    plus_laps = models.IntegerField(blank=True, null=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING)

    race = models.ForeignKey(Races, models.DO_NOTHING)

    team = models.ForeignKey('Teams', models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'races_drivers'





class ReportResponses(models.Model):

    id = models.UUIDField(primary_key=True)

    content = models.TextField()

    video_path = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)

    from_driver = models.ForeignKey(Drivers, models.DO_NOTHING, db_column='from_driver', blank=True, null=True)

    report = models.ForeignKey('Reports', models.DO_NOTHING, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'report_responses'





class ReportTargets(models.Model):

    id = models.UUIDField(primary_key=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING, blank=True, null=True)

    report = models.ForeignKey('Reports', models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'report_targets'





class Reports(models.Model):

    id = models.UUIDField(primary_key=True)

    content = models.TextField()

    video_path = models.TextField()

    from_driver = models.ForeignKey(Drivers, models.DO_NOTHING, db_column='from_driver')

    race = models.ForeignKey(Races, models.DO_NOTHING)

    verdict = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'reports'





class Roles(models.Model):

    id = models.UUIDField(primary_key=True)

    name = models.CharField(unique=True, max_length=54, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'roles'





class Seasons(models.Model):

    id = models.UUIDField(primary_key=True)

    name = models.CharField(unique=True, max_length=50, blank=True, null=True)

    fia_role = models.ForeignKey(Roles, models.DO_NOTHING, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'seasons'





class SeasonsDrivers(models.Model):

    id = models.UUIDField(primary_key=True)

    is_reserve = models.BooleanField(blank=True, null=True)

    driver = models.ForeignKey(Drivers, models.DO_NOTHING)

    season = models.ForeignKey(Seasons, models.DO_NOTHING)

    team = models.ForeignKey('Teams', models.DO_NOTHING, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'seasons_drivers'

        unique_together = (('driver', 'season'),)





class Teams(models.Model):

    id = models.UUIDField(primary_key=True)

    name = models.CharField(unique=True, max_length=100)

    color = models.CharField(max_length=7, blank=True, null=True)

    icon = models.TextField(blank=True, null=True)

    logo = models.TextField(blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'teams'





class Tracks(models.Model):

    id = models.UUIDField(primary_key=True)

    name = models.CharField(max_length=50)

    flag = models.TextField(blank=True, null=True)

    image = models.TextField(blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'tracks'





class Users(models.Model):

    id = models.UUIDField(primary_key=True)

    username = models.CharField(unique=True, max_length=50)

    password = models.BinaryField()

    driver = models.OneToOneField(Drivers, models.DO_NOTHING, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'users'





class UsersRoles(models.Model):

    id = models.UUIDField(primary_key=True)

    user = models.ForeignKey(Users, models.DO_NOTHING)

    role = models.ForeignKey(Roles, models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'users_roles'

