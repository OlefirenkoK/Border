from django.db import models
from os import *

# Create your models here.


def update_filename_crt(upload_path):

    def make_tt_number(TT) :

        if TT < 10 :
            return '00' + str(TT)
        elif TT >= 10 and TT < 100 :
            return '0' + str(TT)
        else:
            return str(TT)

    def wraper(instance, filename) :

        ext = filename.split('.')[-1]
        filename_new = make_tt_number(instance.tt.idTT) + '.' + ext
        all_path = path.join(upload_path, filename_new)

        return all_path

    return wraper

class MainTtModel(models.Model) :

    class Meta () :

        db_table = 'main'

    CHOICE = (
        (1, 'Open') ,
        (2, 'Close') ,
        (3, 'InProgress') ,
    )

    idTT = models.IntegerField(unique=True)
    city = models.CharField(max_length=30, blank=True)
    address = models.CharField(max_length=120, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    wireless = models.CharField(max_length=20, blank=True)
    wiredProvider = models.CharField(max_length=30, blank=True)
    contractId = models.CharField(max_length=30, blank=True)
    supportCont1 = models.CharField(max_length=50, blank=True)
    status = models.IntegerField(choices=CHOICE, default="Open")

class AdditionInfoTtModel(models.Model) :

    """
    Model for additional information ;
    has foreign key with model Main
    col NetworkInfo : GetWay if static ; mac if dhcp ; username password if PPPoE ; all inf if another .
    """

    class Meta () :
        db_table = 'additionInfo'

    CHOICE_NETWORK_TYPE = (
        (1, 'Another'),
        (2, 'dhcp'),
        (3, 'static'),
        (4, 'PPPoE'),
    )

    tt = models.ForeignKey(MainTtModel)
    wiredSimNumb = models.CharField(max_length=20, blank=True)
    supportCont2 = models.CharField(max_length=50, blank=True)
    region = models.CharField(max_length=20, blank=True, null=True)

    networkType = models.IntegerField(choices=CHOICE_NETWORK_TYPE , default="Another")
    ovpnMac = models.CharField(max_length=20, blank=True, null=True)
    wanIp = models.CharField(max_length=20, blank=True, null=True)
    NetworkInfo = models.TextField(max_length=60, blank=True)

    WirelessType = models.CharField(max_length=40, blank=True)


#Not a model
class CityModel (models.Model) :

    class Meta :
        db_table = 'Cities'

    city = models.CharField(max_length=30)

class CitiesModel (models.Model) :

    class Meta :
        db_table = 'cities'

    city = models.CharField(max_length=30)

class WiredProvirerModel(models.Model) :

    class Meta :
        db_table = 'wiredprovider'

    wiredProvider = models.CharField(max_length=30)

class WirelessModel (models.Model) :

    class Meta :
        db_table = 'wirelessProvider'

    wireless = models.CharField(max_length=30)

class FilesModel (models.Model) :

    class Meta :
        db_table = 'files'

    tt = models.ForeignKey(MainTtModel)
    crt = models.FileField(upload_to=update_filename_crt('crt/'))
    key = models.FileField(upload_to=update_filename_crt('key/'))
    backup = models.FileField(upload_to=update_filename_crt('backup/'))

    def delete(self, *args, **kwargs) :

        if kwargs['row'] == 'crt' :
            storage, path = self.crt.storage, self.crt.path
            storage.delete(path)
        elif kwargs['row'] == 'key' :
            storage, path = self.key.storage, self.key.path
            storage.delete(path)
        elif kwargs['row'] == 'backup' :
            storage, path = self.backup.storage, self.backup.path
            storage.delete(path)

class LogsModel(models.Model) :

    class Meta :
        db_table = 'logs'

    ACTIONS = {
        1 : 'add' ,
        2 : 'update',
        3 : 'migrate_to',
        4 : 'migrate_from',
        5 : 'verification',
    }

    tt = models.ForeignKey(MainTtModel)
    user = models.CharField(max_length=30)
    action = models.CharField(max_length=400)
    date = models.DateTimeField(auto_now_add=True)

    def create_action(self, act, tt, **kwargs):
        print(act, tt, kwargs)
        def mikrotik() :
            if 'mikrotik' in kwargs :
                if kwargs['mikrotik'] :
                    mikr = 'with mikrotik'
                else:
                    mikr = 'without mikrotik'
            else:
                mikr = ''
            return mikr

        if act == 1:
            self.action = '%s TT%s.' %(self.ACTIONS[act], tt)
        elif act == 2 and 'parameters' in kwargs:
            ld = '%s TT%s \n' %(self.ACTIONS[act], tt)
            for key in kwargs['parameters'] :
                ld += '%s : update from %s to %s \n' %(key, kwargs['parameters'][key][0],
                                                       kwargs['parameters'][key][1])
            if ld != 'TT%s \n' %tt :
                self.action = ld
            else:
                self.action = ld + 'error in logs parameters'
        elif act == 3 and 'migrate_to' in kwargs :
            self.action = 'TT%s %s TT%s %s' %(tt, self.ACTIONS[act], str(kwargs['migrate_to']), mikrotik())
        elif act == 4 and 'migrate_from' in kwargs :
            self.action = 'TT%s %s %s %s' %(tt, self.ACTIONS[act], str(kwargs['migrate_from']), mikrotik())
        elif act == 5 :
            self.action = '%s TT%s' %(self.ACTIONS[act], tt)
        else:
            raise ValueError

print('TEST')
