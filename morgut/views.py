from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import render_to_response , redirect
from django.core.context_processors import csrf
from django.contrib import auth
from morgut.forms import MainTtForm, AdditionTtForm, MigrateForm
from morgut.models import MainTtModel, AdditionInfoTtModel, CitiesModel, WiredProvirerModel , \
    WirelessModel, FilesModel, LogsModel
from django.core.exceptions import ObjectDoesNotExist
import simplejson
from paramiko import *
import datetime
import os
from Boarder.settings import MEDIA_ROOT
from time import sleep
from re import findall
from django.core.paginator import Paginator

# Create your views here.

class TT :

    __instance = None
    __count = 0
    idTT = []
    cities = []
    wireds = []
    wireless = []

    def __new__(cls, *args, **kwargs):

        if cls.__instance is None:
            cls.__instance = super(TT, cls).__new__(TT)
        return cls.__instance

    def __init__(self):

        if self.__instance is not None:
            if TT.__count == 0 :
                get_Cities = CitiesModel.objects.values('city')
                get_Provider = WiredProvirerModel.objects.values('wiredProvider')
                get_Wireless = WirelessModel.objects.values('wireless')
                get_idTT = MainTtModel.objects.values('idTT')
                TT.cities = [city['city'] for city in get_Cities]
                TT.wireds = [wired['wiredProvider'] for wired in get_Provider]
                TT.wireless = [wireless['wireless'] for wireless in get_Wireless]
                TT.idTT = [idtt['idTT'] for idtt in get_idTT]
            TT.__count = 1

    def get_id(self, **kwargs):

        if self.__instance != None :

            if 'JSON' in kwargs :
                return JsonResponse(self.idTT, safe=False)

            return self.idTT

    def set_id(self, id_tt):

        if self.__instance != None :
            try:
                self.idTT.append(int(id_tt))
            except:
                print('Error id_tt is not integer')
        else:
            print('Some bug in TT.set_id()')

    def get_cities(self, **kwargs):

        if self.__instance is not None:
            if 'JSON' in kwargs:
                return  JsonResponse(self.cities, safe=False)

            return self.cities

    def set_sities(self, city): ## :))

        if self.__instance is not None:
            model_cities = CitiesModel(city=city)
            model_cities.save()
            print('City was added')
            self.cities.append(city)

    def get_wired(self, **kwargs):

        if self.__instance is not None:
            if 'JSON' in kwargs:
                return JsonResponse(self.wireds, safe=False)

            return self.wireds

    def set_wired(self, wired):

        if self.__instance is not None:
            model_wireds = WiredProvirerModel(wiredProvider=wired)
            model_wireds.save()
            print('Provider was added')
            self.wireds.append(wired)

    def get_wireless(self, **kwargs):

        if self.__instance != None :
            if 'JSON' in kwargs :
                return JsonResponse(self.wireless, safe=False)

            return self.wireless

    def set_wireless(self , wireless):

        if self.__instance != None :
            model_wireless = WirelessModel(wireless=wireless)
            model_wireless.save()
            self.wireless.append(wireless)
            print('Wireless was added')

    def verification(self, *args):

        if len(args) == 2 :
            if args[0] == 'city' :
                if args[1] not in TT.get_cities(self) :
                    TT.set_sities(self, args[1])
            if args[0] == 'wireless' :
                if args[1] not in TT.get_wireless(self) :
                    TT.set_wireless(self , args[1])
            if args[0] == 'wiredProvider' :
                if args[1] not in TT.get_wired(self) :
                    TT.set_wired(TT, args[1])
        else:
            print('len *args must be 2')

class SshConnect :

    def __init__(self):

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())

    def __del__(self):

        self.ssh.close()
        print('ssh close')

    def connect_ssh(self, host, port=22, name='USER', passwd='xxx'):

        try:
            self.ssh.connect(hostname=host, port=port, username=name, password=passwd)
            print('ssh connected')
        except OSError :
            raise ValueError

    def connect_sftp(self, host, port=22, name='USER', passwd='xxx'):

        transport = Transport((host, port))
        transport.connect(username=name, password=passwd)
        self.sftp = SFTPClient.from_transport(transport)
        print('sftp connected')

    def sftp_put(self, Ldirect, Rdirect):

        self.sftp.put(Ldirect, Rdirect)

    def sftp_get(self, Rdirect, Ldirect):

        self.sftp.get(Rdirect, Ldirect)

    def easy_execute(self, command, wait=True):

        stdin, stdout, stderr = self.ssh.exec_command(command)

        if wait :
            return stdout.readlines()

    @staticmethod
    def make_domain(tt) :

        DOMAIN = '.tt.kf.lo'

        if type(tt) is str :
            try:
                TT = int(tt)
            except:
                raise ValueError
        elif type(tt) is int :
            TT = tt
        else:
            raise ValueError

        if TT < 10:
            return '00' + str(TT) + DOMAIN
        elif TT >= 10 and TT < 100:
            return '0' + str(TT) + DOMAIN
        else:
            return str(TT) + DOMAIN

    @staticmethod
    def make_path(path, TT, ext='backup'):

        if type(TT) is int :

            if TT < 10 :
                tt = '00' + str(TT)
            elif TT >= 10 and TT < 100 :
                tt = '0' + str(TT)
            else:
                tt = str(TT)

            return os.path.join(path + ext, tt + '.' + ext)


class Mikrotik(SshConnect) :

    pattern = {
        'certificate_find' : r'^\D*(\d+).*name="(.*?)"',
        'ovpn_interface' : r'name="(.*?)"',
        'ppp_interface' : r'name="(.*?)".*port=usb',
        'ip_iface' : r'[^X|x]\s+([\d{1,3}\.]+\d{1,3}\/\d{1,2})\D*[\d{1,3}\.]+\d{1,3}\W*(.*)',
        'static' : r'^\s+\d*\s*[^X|I|D]\s+([\d{1,3}\.]+\d{1,3}\/\d{1,2})\D*[\d{1,3}\.]+\d{1,3}\W*(.*)',
        'mac' : r'mac-address=([\w{2}:]+)',
        'apn' : r'\'\s+[\d]*\s+[^X]\s+name="(.*?)"'
    }

    def __init__(self, old, new):

        if type(old) is not int or type(new) is not int :
            raise ValueError

        SshConnect.__init__(self)
        self.old = old
        self.new = new
        self.id_old = MainTtModel.objects.get(idTT=self.old).__dict__['id']
        self.id_new = MainTtModel.objects.get(idTT=self.new).__dict__['id']
        self.identify_old = Mikrotik.tt_identify(old)
        self.identify_new = Mikrotik.tt_identify(new)

    def get_files_model(self, number):
        print(number)
        try:
            files_model = FilesModel.objects.get(tt_id=number)
        except ObjectDoesNotExist:
            model = FilesModel(tt_id=number)
            model.save()
            print('test')
            files_model = FilesModel.objects.get(tt_id=number)
        return files_model

    def make_name(self, ext='backup', old=True):

        if old :
            tt = self.identify_old
        else:
            tt = self.identify_new

        now = datetime.datetime.now()
        time_create = datetime.datetime.date(now).__str__() + '-' + datetime.datetime.time(now).__str__().split('.')[0]
        name_create = 'p' + tt + '.' + time_create + '.' + ext

        return name_create

    def create_file_name(self, identify ,ext='backup'):

        if type(identify) is str:
            return os.path.join('%s/' %ext, identify + '.' + ext)
        else:
            raise ValueError

    def create_file_path(self, local_path, ext='backup'):

        if type(local_path) is str :
            MEDIA = MEDIA_ROOT

            return os.path.join(MEDIA, local_path)
        else:
            raise ValueError

    def get_certficete(self):

        answer = self.easy_execute('certificate print')
        certificates = {}
        pattern = self.pattern['certificate_find']
        for line in answer :
            string = line.rstrip()
            cert = findall(pattern, string)
            if cert :
                if len(cert[0]) == 2 :
                    certificates[cert[0][0]] = cert[0][1]

        return certificates

    def verif_new_cert(self, old , new):

        ver = ( set(old)^set(new) )
        if ver :
            return new[list(ver)[0]]
        else:
            return False

    def ovpn_client_interface(self):

        answer = self.easy_execute('interface ovpn-client print')
        KF_VPN = []
        pattern = self.pattern['ovpn_interface']
        for line in answer :
            string = line.rstrip()
            kf_vpn = findall(pattern, string)
            if kf_vpn :
                if len(kf_vpn) == 1 :
                    KF_VPN.append(kf_vpn)

        return KF_VPN[0]

    @staticmethod
    def get_commands(arg):

        commands = {
            'create_backup' : lambda x : 'system backup save name={}'.format(x),
            'create_certificate' : lambda x : 'certificate import file-name={} passphrase={}'.format(x, x.split('.')[0]),
            'set_ovpn_cert' : lambda x, y: 'interface ovpn-client set {} certificate={}'.format(x, y),
            'set_identity' : lambda x: 'system identity set name=p{}.mhs.kiev.ua'.format(x),
            'get_mac' : lambda x: 'interface print detail where name={}'.format(x),
            'get_apn' : lambda x: 'interface ppp-client print detail from={}'.format(x),
        }

        if arg in commands :
            return commands[arg]
        else:
            return False

    @staticmethod
    def tt_identify(number):

        if type(number) is int and number > 0:

            if number < 10 :
                return '00' + str(number)
            elif number >= 10 and number < 100 :
                return '0' + str(number)
            else:
                return str(number)

        else:
            raise ValueError


class MikrotikVerificate(Mikrotik) :

    def __init__(self, number):

        SshConnect.__init__(self)
        if type(number) is str and int(number) :
            self.number = number
        else:
            raise ValueError
        self.identify = Mikrotik.tt_identify(int(number))

    def get_iface(self, command , pattern):

        answer = self.easy_execute(command)
        iface = []
        for line in answer :
            string = line.rstrip()
            local = findall(pattern, string)
            if len(local) == 1 :
                iface.append(local[0])

        return iface

    def type_iface(self, wan):

        if type(wan) is not list :
            raise ValueError
        if len(wan) == 0:
            return None
        elif len(wan) == 1:
            string = self.easy_execute('ip dhcp-client print')
            if findall(r'%s' %wan[0], string.__str__()) :
                return 'DHCP'
            string = self.easy_execute('interface pppoe-client print where name=%s' %wan[0])
            if findall(r'%s' %wan[0], string.__str__()) :
                return 'PPPoE'
            string = self.easy_execute('ip address print where interface=%s' %wan[0])
            if findall(Mikrotik.pattern['static'], string.__str__()) :
                return 'Static'

            return 'Another'
        else:
            return False

    def get_mac(self, iface):

        if type(iface) is not list and len(iface) != 1 :
            raise ValueError
        string = self.easy_execute(Mikrotik.get_commands('get_mac')(iface[0])).__str__()
        pattern = findall(Mikrotik.pattern['mac'], string)
        if len(pattern) == 1 :
            return pattern[0]
        else:
            return False

    def get_apn(self, iface):

        if type(iface) is not list:
            raise ValueError
        apn = []
        pattern = Mikrotik.pattern['apn']
        for face in iface:
            string = self.easy_execute(Mikrotik.get_commands('get_apn')(face)).__str__()
            print(string)
            local = findall(pattern, string)
            print(local)
            if local:
                apn_local = findall(r'apn="(.*?)"', string)
                if apn_local:
                    apn.append(apn_local[0])
        print(apn, 'apn')
        if len(apn) == 1 :
            return apn[0]
        elif len(apn) >= 2:
            return apn.__str__()
        else:
            return False

    @staticmethod
    def get_ip_iface(ip, ovpn, ppp, bridge):

        ip_set = set(ip)
        all = set().union(ovpn, ppp, bridge)
        iface = ip_set.difference(all)

        return list(iface)


def board(request) :

    args = {}
    args.update(csrf(request))
    args['username'] = auth.get_user(request).username
    args['TTs'] = MainTtModel.objects.all().order_by('idTT')

    return render_to_response('board.html', args)

def addNew(request) :

    args = {}
    tt = TT()
    args.update(csrf(request))
    args['username'] = auth.get_user(request).username
    args['mform'] = MainTtForm
    args['aform'] = AdditionTtForm
    if request.POST :
        mform = MainTtForm(request.POST)
        aform = AdditionTtForm(request.POST)
        if mform.is_valid() and aform.is_valid():
            array_id_tt_saved = MainTtModel.objects.values('idTT')
            id_tt_saved = [i['idTT'] for i in array_id_tt_saved]
            try:
                get_idTT = int(request.POST.get('idTT'))
            except TypeError:
                args['error'] = 'Wrong! Must be integer'
                return render_to_response('addNew.html', args)
            if get_idTT in id_tt_saved:

                return HttpResponse('Wrong! This TT is exist')
            else:
                idTT = mform.save()
                addition = aform.save(commit=False)
                addition.tt = idTT
                addition.save()
                log = LogsModel()
                log.tt_id = idTT.id
                log.user = args['username']
                log.create_action(act=1, tt=str(idTT.idTT))
                log.save()
                if request.POST.get('city') not in tt.get_cities():
                    tt.set_sities(request.POST.get('city'))
                if request.POST.get('wiredProvider') not in tt.get_wired():
                    tt.set_wired(request.POST.get('wiredProvider'))
                if int(request.POST.get('idTT')) not in tt.get_id() :
                    tt.set_id(int(request.POST.get('idTT')))
                if request.POST.get('wireless') not in tt.get_wireless():
                    tt.set_wireless(request.POST.get('wireless'))

                return HttpResponse('success')
        else :
            args['cities'] = tt.get_cities()
            args['wireds'] = tt.get_wired()
            args['error'] = "Form isn't valid!!!"
            return HttpResponse("Form isn't valid!!!")

    else:
        args['cities'] = tt.get_cities()
        args['wireds'] = tt.get_wired()
        return render_to_response('addNew.html', args)

def tt_info (request, tt_id) :

    args = {}
    args.update(csrf(request))
    args['username'] = auth.get_user(request).username
    main_model = MainTtModel.objects.get(idTT=tt_id)
    addition_model = AdditionInfoTtModel.objects.get(tt_id=main_model.__dict__['id'])
    args['main'] = main_model
    args['addition'] = addition_model
    args['migrate'] = MigrateForm()

    if request.POST or request.FILES:

        if request.FILES :
            print(request.FILES)
            CRT = request.FILES.get('upload-crt', None)
            KEY = request.FILES.get('upload-key', None)
            BACKUP = request.FILES.get('upload-backup', None)
            try:
                files_tt = FilesModel.objects.get(tt_id=main_model.__dict__['id'])

                if CRT != None :
                    if CRT.name[-4 :] == '.crt':
                        if files_tt.crt.name :
                            files_tt.delete(row='crt')
                        files_tt.crt = CRT

                if KEY != None :
                    if KEY.name[-4 :] == '.key':
                        if files_tt.key.name :
                            files_tt.delete(row='key')
                        files_tt.key = KEY

                if BACKUP != None :
                    if BACKUP.name[-7 :] == '.backup':
                        if files_tt.backup.name :
                            files_tt.delete(row='backup')
                        files_tt.backup = BACKUP

            except ObjectDoesNotExist :
                files_tt = FilesModel(crt=CRT, key=KEY, backup=BACKUP, tt_id=main_model.__dict__['id'])

            files_tt.save()

        if request.POST :

            print(request.POST)
            json_main = request.POST.get('main', '')
            main = simplejson.loads(json_main)
            parameter = {}

            if main :
                tt = TT()
                for key in main :
                    parameter[key] = [main_model.__dict__[key]]
                    main_model.__dict__[key] = main[key]
                    parameter[key].append(main[key])
                    tt.verification(key, main[key])
                main_model.save()

            json_addition = request.POST.get('addition' , '')
            addition = simplejson.loads(json_addition)
            if addition :
                for key in addition :
                    parameter[key] = [addition_model.__dict__[key]]
                    addition_model.__dict__[key] = addition[key]
                    parameter[key].append(addition[key])
                addition_model.save()

            log = LogsModel()
            log.tt_id = main_model.id
            log.user = args['username']
            log.create_action(act=2, tt=str(tt_id), parameters=parameter)
            log.save()

        return HttpResponse('success')

    else:

        return render_to_response('ttInfo.html', args)

def update_tt(request) :

    if request.POST :
        tt = TT()
        try:
            ttid = int(request.POST.get('idTT'))
        except :
            return HttpResponse('ajaxError')

        parameter = {}

        if ttid in tt.idTT :
            transform = {'city' : 'city',
                         'addr' : 'address',
                         'phone' : 'phone',
                         'wireless' : 'wireless',
                         'wired' : 'wiredProvider',
                         'contract' : 'contractId',
                         'support' : 'supportCont1'}
            col = request.POST.get('column')
            val = request.POST.get('value')
            tt_info = MainTtModel.objects.get(idTT=ttid)
            parameter[transform[col]] = [tt_info.__dict__[transform[col]]]
            tt_info.__dict__[transform[col]] = val
            tt_info.save()
            log = LogsModel()
            log.user = auth.get_user(request).username
            log.tt_id = tt_info.id
            parameter[transform[col]].append(val)
            log.create_action(act=2, tt=str(ttid), parameters=parameter)
            log.save()

            if col == 'city' :
                if val not in tt.get_cities() :
                    tt.set_sities(val)
            if col == 'wireless' :
                if val not in tt.get_wireless() :
                    tt.set_wireless(val)
            if col == 'wired' :
                if val not in tt.get_wired() :
                    tt.set_wired(val)

            return HttpResponse('success')
        else:
            return HttpResponse('id is not in DB')
    else:
        return HttpResponse('ajaxError')

def get_ICWW (request) :

    tt = TT()
    idTT = tt.get_id()
    city = tt.get_cities()
    wired = tt.get_wired()
    wireless = tt.get_wireless()

    json = {
        'idTT' : idTT,
        'city' : city,
        'wired' : wired,
        'wireless' : wireless
    }
    JSON = JsonResponse(json, safe=False)

    return HttpResponse(JSON)

def get_item(request) :

    args = {}

    if request.POST :

        tt = TT()
        item = request.POST.get('item')
        if item == 'city' :
            city = tt.get_cities(JSON=True)
            return HttpResponse(city)

        elif item == 'wireless' :
            wireless = tt.get_wireless(JSON=True)
            return HttpResponse(wireless)

        elif item == 'wired' :
            wired = tt.get_wired(JSON=True)
            return HttpResponse(wired)

        else:
            args['error'] = 'Incorrect request, %s does not exist' %item
            error = JsonResponse(args, safe=False)

            return HttpResponse(error)
    else:
        args['error'] = 'request must be POST'
        error = JsonResponse(args, safe=False)

        return HttpResponse(error)

def update_item(request, tt_id) :

    args = {}
    parameter = {}
    if request.POST :

        try:
            main = MainTtModel.objects.get(idTT=int(tt_id))
        except:
            args['error'] = 'TT is not in MainModel'
            responce = JsonResponse(args)

            return HttpResponse(responce)

        item_column = request.POST.get('column', None)
        item_value = request.POST.get('value', '')

        if (set({item_column}) & set(main.__dict__)) :

            tt = TT()
            parameter[item_column] = [main.__dict__[item_column]]
            main.__dict__[item_column] = item_value
            parameter[item_column].append(item_value)
            args['success'] = item_value
            responce = JsonResponse(args)
            main.save()
            tt.verification(item_column, item_value)
            log = LogsModel()
            log.tt_id = main.id
            log.user = auth.get_user(request).username
            log.create_action(act=2, tt=str(tt_id), parameters=parameter)
            log.save()

            return HttpResponse(responce)

        try:
            addition = AdditionInfoTtModel.objects.get(tt_id=main.__dict__['id'])
        except:
            args['error'] = 'TT is not in AdditionInfoTtModel'
            responce = JsonResponse(args)

            return HttpResponse(responce)

        if (set({item_column}) & set(addition.__dict__)) :

            parameter[item_column] = [addition.__dict__[item_column]]
            addition.__dict__[item_column] = item_value
            parameter[item_column].append(item_value)
            args['success'] = item_value
            print(item_column, item_value)
            addition.save()
            responce = JsonResponse(args)
            log = LogsModel()
            log.tt_id = main.id
            log.user = auth.get_user(request).username
            log.create_action(act=2, tt=str(tt_id), parameters=parameter)
            log.save()

            return HttpResponse(responce)

        else:
            args['error'] = 'Some bug call dev'

            return HttpResponse(args['error'])

    else:
        args['error'] = 'Request must be POST'

        return HttpResponse(args['error'])

def download_file(request, tt_id) :

    if request.POST :

        crt_request = request.POST.get('crt', '')
        key_request = request.POST.get('key', '')
        backup_request = request.POST.get('backup', '')

        try:
            main = MainTtModel.objects.get(idTT=tt_id)
            file_model = FilesModel.objects.get(tt_id=main.id)

            if crt_request == 'true' :
                file = file_model.crt
            elif key_request == 'true' :
                file = file_model.key
            elif backup_request == 'true' :
                file = file_model.backup
            else:
                file = None
            if file != None and file.name != '':

                return HttpResponse(file)
        except :
            print('Request for download files is incorrect %s , %s' %(request, tt_id))

def migrate_tt(request, tt_id) :

    def error_dry() :

        args.update(csrf(request))
        args['username'] = auth.get_user(request).username
        main_model = MainTtModel.objects.get(idTT=tt_id)
        addition_model = AdditionInfoTtModel.objects.get(tt_id=main_model.__dict__['id'])
        args['main'] = main_model
        args['addition'] = addition_model
        args['migrate'] = MigrateForm()

    args = {}

    if request.POST :
        form = MigrateForm(request.POST)
        if form.is_valid() :
            mikrotik = request.POST.get('mikrotik' , None)
            new_tt = request.POST.get('new_tt', None)
            try:
                int(new_tt)
            except:
                args['error'] = 'New TT number nust be integer not %s' %new_tt
                error_dry()

                return render_to_response('ttInfo.html', args)

            if new_tt is not None :
                if form.migrate_save(new=new_tt, old=tt_id) :
                    log = LogsModel()
                    log.user = auth.get_user(request).username
                    new_tt_log = LogsModel()
                    new_tt_log.user = auth.get_user(request).username
                    log.tt_id = MainTtModel.objects.get(idTT=tt_id).id
                    new_tt_log.tt_id = MainTtModel.objects.get(idTT=tt_id).id

                    if mikrotik != None :

                        migrate_mikr = Mikrotik(old=int(tt_id), new=int(new_tt))
                        try:
                            migrate_mikr.connect_ssh(host=SshConnect.make_domain(tt_id)) 
                            migrate_mikr.connect_sftp(host=SshConnect.make_domain(tt_id))
                        except :
                            args['error'] = 'Server cannot connection to TT%s' %(str(tt_id))
                            error_dry()

                            return render_to_response('ttInfo.html', args)

                        backup_old_name = migrate_mikr.make_name()
                        migrate_mikr.easy_execute(command=Mikrotik.get_commands('create_backup')(backup_old_name))
                        exist_files = migrate_mikr.get_files_model(migrate_mikr.id_old)
                        if exist_files.backup : 
                            print('file exist')
                            os.remove(exist_files.backup.path)
                            migrate_mikr.sftp_get(backup_old_name, exist_files.backup.path)
                        else:
                            print('file dont exist')
                            backup_name = migrate_mikr.create_file_name(migrate_mikr.identify_old)
                            upload_path = migrate_mikr.create_file_path(backup_name)
                            migrate_mikr.sftp_get(backup_old_name, upload_path)
                            
                        new_files = migrate_mikr.get_files_model(migrate_mikr.id_new)

                        if new_files.crt.name and new_files.key.name :
                            upload_crt_name = os.path.basename(new_files.crt.name)
                            upload_key_name = os.path.basename(new_files.key.name)
                            cert_old = migrate_mikr.get_certficete()
                            migrate_mikr.sftp_put(new_files.crt.path, upload_crt_name)
                            migrate_mikr.sftp_put(new_files.key.path, upload_key_name)
                            sleep(4)
                            migrate_mikr.easy_execute(Mikrotik.get_commands('create_certificate')(upload_crt_name))
                            sleep(1)
                            migrate_mikr.easy_execute(Mikrotik.get_commands('create_certificate')(upload_key_name))
                            cert_new = migrate_mikr.get_certficete()
                            cert_add = migrate_mikr.verif_new_cert(cert_old, cert_new)
                            if cert_add:
                                ovpn_iface = migrate_mikr.ovpn_client_interface()
                                if len(ovpn_iface) != 1 :
                                    args['error'] = 'TT%s has %s interfaces!!!' %(migrate_mikr.identify_old, ovpn_iface)
                                    error_dry()

                                    return render_to_response('ttInfo.html', args)
                                
                                migrate_mikr.easy_execute(Mikrotik.get_commands('set_identity')(migrate_mikr.identify_new))
                                migrate_mikr.easy_execute(Mikrotik.get_commands('set_ovpn_cert')(ovpn_iface[0], cert_add),
                                                          wait=False)
                                print('before sleep')
                                sleep(2)
                                print('sleep')
                                migrate_mikr.__del__()
                                print('del')
                            else:
                                args['error'] = 'New certificate has not been created!!!'
                                error_dry()

                                return render_to_response('ttInfo.html', args)

                        else:
                            error = []
                            if not new_files.crt.name :
                                error.append('CRT')
                            if not new_files.key.name :
                                error.append('KEY')
                            args['error'] = error.__str__()
                            error_dry()

                            return render_to_response('ttInfo.html', args)

                        log.create_action(act=3, tt=str(tt_id), migrate_to=str(new_tt), mikrotik=True)
                        new_tt_log.create_action(act=4, tt=str(new_tt), migrate_from=str(tt_id), mikrotik=True)

                    else:
                        print('log create True')
                        log.create_action(act=3, tt=str(tt_id), migrate_to=str(new_tt), mikrotik=False)
                        new_tt_log.create_action(act=4, tt=str(new_tt), migrate_from=str(tt_id), mikrotik=False)
                    log.save()
                    new_tt_log.tt_id = MainTtModel.objects.get(idTT=new_tt).id
                    new_tt_log.save()

                    return redirect('/list/tt_info/%s/' %new_tt)

                else:
                    args['error'] = 'Error in creation new TT%s' %new_tt
                    error_dry()

                    return render_to_response('ttInfo.html', args)
            else:
                args['error'] = 'New TT%s is not correct' %new_tt
                error_dry()

                return render_to_response('ttInfo.html', args)
        else:
            args['error'] = 'Request must be post'
            error_dry()

            return render_to_response('ttInfo.html', args)

def verificate_tt(request):

    def error_dry(error) :

        args['error'] = error
        responce = JsonResponse(args)

        return HttpResponse(responce)

    def choice(ch, resp) :

        for i in ch :
            print(i[1].upper(), resp.upper())
            if i[1].upper() == resp.upper() :
                print(i[0])
                return i[0]
        raise ValueError

    args = {}
    json = {}
    args['username'] = auth.get_user(request).username

    if request.POST :
        tt_id = request.POST.get('tt_id', None)
        if tt_id == None :
            responce = error_dry('Incorrect TT ID number')

            return responce
        try:
            mikrotik = MikrotikVerificate(number=tt_id)
            mikrotik.connect_ssh(host=SshConnect.make_domain(int(mikrotik.number))
            KF_VPN = mikrotik.get_iface('interface ovpn-client print', Mikrotik.pattern['ovpn_interface'])
            bridge_local = mikrotik.get_iface('interface bridge print', Mikrotik.pattern['ovpn_interface'])
            ppp_3g = mikrotik.get_iface('interface ppp-client print', Mikrotik.pattern['ppp_interface'])
            ip_iface = mikrotik.get_iface('ip address print', Mikrotik.pattern['ip_iface'])
            iface = dict([(i[1], i[0]) for i in ip_iface])
            wan_iface = mikrotik.get_ip_iface(ip=iface, ovpn=KF_VPN, ppp=ppp_3g, bridge=bridge_local)
            if len(wan_iface) == 1 :
                json['wan_ip'] = iface[wan_iface[0]]
                try:
                    network_type = mikrotik.type_iface(wan_iface)
                except ValueError:
                    responce = error_dry('Value error in network_type')
                    return responce
                if network_type :
                    json['networkType'] = network_type
                else:
                    json['networkType'] = False
            elif len(wan_iface) == 0:
                json['networkType'] = False
                json['wan_ip'] = ''
            else:
                json['networkType'] = False
                json['wan_ip'] = [i for i in wan_iface].__str__()
            try:
                mac = mikrotik.get_mac(KF_VPN)
            except ValueError:
                responce = error_dry('ValueError in mac')
                return responce
            json['ovpnMac'] = mac
            try:
                apn = mikrotik.get_apn(ppp_3g)
            except ValueError:
                responce = error_dry('ValueError in apn')
                return responce
            if apn:
                json['WirelessType'] = apn
            else:
                json['WirelessType'] = ''
            main_model = MainTtModel.objects.get(idTT=tt_id)
            file_model = mikrotik.get_files_model(main_model.id)
            mikrotik.identify_old = mikrotik.identify
            backup_name = mikrotik.make_name()
            backup_full_name = mikrotik.create_file_name(mikrotik.identify)
            backup_path = mikrotik.create_file_path(backup_full_name)
            mikrotik.easy_execute(command=mikrotik.get_commands('create_backup')(backup_name))
            if file_model.backup :
                os.remove(file_model.backup.path)
            mikrotik.connect_sftp(host=SshConnect.make_domain(int(mikrotik.number)))
            mikrotik.sftp_get(backup_name, backup_path)
            file_model.backup = backup_full_name
            file_model.save()
            addition_model = AdditionInfoTtModel.objects.get(tt_id=main_model.id)
            try:
                addition_model.networkType = choice(AdditionInfoTtModel.CHOICE_NETWORK_TYPE, json['networkType'])
            except ValueError:
                responce = error_dry('local_error in AdditionInfoTtModel.CHOICE_NETWORK_TYPE')
                return responce
            addition_model.ovpnMac = json['ovpnMac']
            addition_model.WirelessType = json['WirelessType']
            addition_model.save()
            log = LogsModel()
            log.tt_id = main_model.id
            log.user = args['username']
            log.create_action(act=5, tt=str(main_model.idTT))
            log.save()

        except ValueError:
            responce = error_dry('Error in Create mikrotik object')

            return responce

        responce = JsonResponse({'success' : json})

        return HttpResponse(responce)
    else:
        args['error'] = 'Request must be POST'
        responce = JsonResponse(args)

        return HttpResponse(responce)

def tt_history(request, tt_id, page_number) :

    args = {}
    args.update(csrf(request))
    main_model = MainTtModel.objects.get(idTT=tt_id)
    log_model = LogsModel.objects.filter(tt_id=main_model.id)
    current_page = Paginator(log_model, 8)
    args['main'] = main_model
    args['username'] = auth.get_user(request).username
    args['log'] = current_page.page(page_number)

    return render_to_response('tt-history.html', args)
