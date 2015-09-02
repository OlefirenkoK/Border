from django import forms
from morgut.models import MainTtModel, AdditionInfoTtModel

#from morgut.views import City


class MainTtForm(forms.ModelForm) :


    class Meta() :

        model = MainTtModel
        fields = ['idTT', 'city', 'address', 'phone', 'wireless',
                  'wiredProvider', 'contractId', 'supportCont1', 'status']
        widgets = {
            'city' : forms.TextInput(attrs={'list' : 'city_list',
                                            'autocomplete' : 'off',
                                            }),
            'wireless' : forms.TextInput(attrs={'list' : 'wireless_list',
                                                'autocomplete' : 'off',
                                                }),

            'wiredProvider' : forms.TextInput(attrs={'list' : 'wiredProvider_list',
                                                     'autocomplete' : 'off',
                                                     }),
        }

class AdditionTtForm(forms.ModelForm) :

    class Meta () :

        model = AdditionInfoTtModel
        fields = ['wiredSimNumb', 'supportCont2', 'region', 'networkType', 'ovpnMac', 'wanIp' , 'NetworkInfo', 'WirelessType']

        widgets = {
            'wiredSimNumb' : forms.TextInput(attrs={'size' : 50}),
            'NetworkInfo' : forms.Textarea(attrs={'cols' : 35, 'rows' : 5}),
            'ovpnMac' : forms.TextInput(attrs={'class' : 'input-mac-address'}),
        }

class MigrateForm(forms.Form) :

    new_tt = forms.IntegerField(min_value=2)
    mikrotik = forms.BooleanField(required=False)

    def migrate_save(self, new, old):

        try:
            main_old = MainTtModel.objects.get(idTT=old)
            try:
                main_new = MainTtModel.objects.get(idTT=new)
                main_new.status = 1
                main_new.wireless = main_old.wireless
            except:
                main_new = MainTtModel(idTT=new,
                                       status=1,
                                       wireless=main_old.wireless)
            main_old.status = 2
            main_old.save()
            main_new.save()
            addition_old = AdditionInfoTtModel.objects.get(tt_id=main_old.id)
            try:
                addition_new = AdditionInfoTtModel.objects.get(tt_id=main_new.id)
                addition_new.wiredSimNumb = addition_old.wiredSimNumb
                addition_new.networkType = addition_old.networkType
                addition_new.ovpnMac = addition_old.ovpnMac
                addition_new.wanIp = ''
                addition_new.region = ''
                addition_new.NetworkInfo = addition_old.NetworkInfo
                addition_new.WirelessType = addition_old.WirelessType
                addition_new.supportCont2 = ''

            except:
                addition_new = AdditionInfoTtModel(tt_id=main_new.id,
                                                   wiredSimNumb=addition_old.wiredSimNumb,
                                                   networkType=addition_old.networkType,
                                                   ovpnMac=addition_old.ovpnMac,
                                                   wanIp='',
                                                   region='',
                                                   NetworkInfo=addition_old.NetworkInfo,
                                                   WirelessType=addition_old.WirelessType,
                                                   supportCont2='')
            addition_new.save()
            addition_old.save()

            return True

        except :

            return False