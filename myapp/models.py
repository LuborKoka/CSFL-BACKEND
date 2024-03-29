# This is an auto-generated Django model module.

# You'll have to do the following manually to clean this up:

#   * Rearrange models' order

#   * Make sure each model has one field with primary_key=True

#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior

#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table

# Feel free to rename the models, but don't rename db_table values or field names.

from django.db import models





class AuthGroup(models.Model):

    name = models.CharField(unique=True, max_length=150)



    class Meta:

        managed = False

        db_table = 'auth_group'





class AuthGroupPermissions(models.Model):

    id = models.BigAutoField(primary_key=True)

    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'auth_group_permissions'

        unique_together = (('group', 'permission'),)





class AuthPermission(models.Model):

    name = models.CharField(max_length=255)

    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)

    codename = models.CharField(max_length=100)



    class Meta:

        managed = False

        db_table = 'auth_permission'

        unique_together = (('content_type', 'codename'),)





class AuthUser(models.Model):

    password = models.CharField(max_length=128)

    last_login = models.DateTimeField(blank=True, null=True)

    is_superuser = models.BooleanField()

    username = models.CharField(unique=True, max_length=150)

    first_name = models.CharField(max_length=150)

    last_name = models.CharField(max_length=150)

    email = models.CharField(max_length=254)

    is_staff = models.BooleanField()

    is_active = models.BooleanField()

    date_joined = models.DateTimeField()



    class Meta:

        managed = False

        db_table = 'auth_user'





class AuthUserGroups(models.Model):

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'auth_user_groups'

        unique_together = (('user', 'group'),)





class AuthUserUserPermissions(models.Model):

    id = models.BigAutoField(primary_key=True)

    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'auth_user_user_permissions'

        unique_together = (('user', 'permission'),)





class DiscordAccounts(models.Model):

    id = models.UUIDField(primary_key=True)

    discord_id = models.BigIntegerField(unique=True)

    discord_username = models.CharField(unique=True, max_length=32)

    discord_global_name = models.CharField(unique=True, max_length=32)

    discord_avatar = models.TextField(blank=True, null=True)

    expires_at = models.DateTimeField()

    user = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)

    refresh_token = models.TextField(blank=True, null=True)

    premium_type = models.IntegerField()

    accent_color = models.TextField(blank=True, null=True)

    banner = models.TextField(blank=True, null=True)

    avatar_decoration = models.TextField(blank=True, null=True)

    banner_color = models.TextField(blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'discord_accounts'





class DjangoAdminLog(models.Model):

    action_time = models.DateTimeField()

    object_id = models.TextField(blank=True, null=True)

    object_repr = models.CharField(max_length=200)

    action_flag = models.SmallIntegerField()

    change_message = models.TextField()

    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)

    user = models.ForeignKey(AuthUser, models.DO_NOTHING)



    class Meta:

        managed = False

        db_table = 'django_admin_log'





class DjangoContentType(models.Model):

    app_label = models.CharField(max_length=100)

    model = models.CharField(max_length=100)



    class Meta:

        managed = False

        db_table = 'django_content_type'

        unique_together = (('app_label', 'model'),)





class DjangoMigrations(models.Model):

    id = models.BigAutoField(primary_key=True)

    app = models.CharField(max_length=255)

    name = models.CharField(max_length=255)

    applied = models.DateTimeField()



    class Meta:

        managed = False

        db_table = 'django_migrations'





class DjangoSession(models.Model):

    session_key = models.CharField(primary_key=True, max_length=40)

    session_data = models.TextField()

    expire_date = models.DateTimeField()



    class Meta:

        managed = False

        db_table = 'django_session'





class Drivers(models.Model):

    id = models.UUIDField(primary_key=True)

    name = models.CharField(unique=True, max_length=50, blank=True, null=True)

    updated_at = models.DateTimeField(blank=True, null=True)



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

    is_dsq = models.BooleanField(blank=True, null=True)



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

    is_dsq = models.BooleanField(blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'races_drivers'

        unique_together = (('race', 'driver'),)





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

    video_path = models.TextField(blank=True, null=True)

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

    race_name = models.TextField()

    emoji = models.CharField(max_length=9, blank=True, null=True)



    class Meta:

        managed = False

        db_table = 'tracks'





class Users(models.Model):

    id = models.UUIDField(primary_key=True)

    username = models.CharField(unique=True, max_length=50)

    password = models.BinaryField()

    driver = models.OneToOneField(Drivers, models.DO_NOTHING, blank=True, null=True)

    discord_account = models.ForeignKey(DiscordAccounts, models.DO_NOTHING, blank=True, null=True)



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

        unique_together = (('user', 'role'),)

