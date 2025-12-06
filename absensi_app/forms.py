import re
from django import forms
from django.core.exceptions import ValidationError

from .models import (
    Pegawai,
    Absensi,
    MasterDepartemen,
    MasterJabatan,
    MasterCabang,
    MasterMesin,
    MasterModeJamKerja,
    ModeJamKerjaJadwal,
)


# ==============================================================================
# FORMS - PEGAWAI
# Form untuk registrasi dan edit data pegawai
# ==============================================================================

class PegawaiForm(forms.ModelForm):
    """Form registrasi pegawai baru dengan User ID otomatis"""

    userid = forms.CharField(
        max_length=20,
        required=True,
        label="User ID",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'id': 'id_userid',
            'autocomplete': 'off',
            'required': 'required',
            'pattern': '[0-9]+',
            'title': 'User ID hanya boleh berisi angka',
            'placeholder': 'Pilih departemen dulu, lalu klik "Generate User ID"',
            'readonly': 'readonly'
        })
    )

    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'contoh@email.com',
            'autocomplete': 'off'
        })
    )

    tanggal_bergabung = forms.DateField(
        required=True,
        label="Tanggal Bergabung",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date',
            'required': 'required'
        })
    )

    class Meta:
        model = Pegawai
        fields = [
            'userid', 'nama_lengkap', 'email', 'nomor_hp', 'alamat', 'tanggal_lahir',
            'departemen', 'jabatan', 'cabang', 'mesin', 
            'mode_jam_kerja',
            'tanggal_bergabung',
        ]
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Masukkan Nama Lengkap',
                'required': 'required'
            }),
            'tanggal_lahir': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nomor_hp': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 081234567890'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Masukkan alamat lengkap'
            }),
            'departemen': forms.Select(attrs={
                'class': 'form-control select2',
                'required': 'required',
                'onchange': 'generateUserID()'
            }),
            'jabatan': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'cabang': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'mesin': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'mode_jam_kerja': forms.Select(attrs={
                'class': 'form-control select2',
                'required': 'required'
            }),
        }

    def clean_userid(self):
        """Validasi User ID: wajib diisi, hanya angka, dan unik"""
        userid = self.cleaned_data.get('userid', '').strip()

        if not userid:
            raise forms.ValidationError(
                "User ID tidak boleh kosong. Pilih departemen dan klik Generate User ID"
            )

        if not userid.isdigit():
            raise forms.ValidationError("User ID hanya boleh berisi angka (0-9)")

        # Cek keunikan hanya saat membuat baru
        if not self.instance.pk and Pegawai.objects.filter(userid=userid).exists():
            raise forms.ValidationError(f"User ID {userid} sudah terdaftar")

        return userid


class PegawaiEditForm(forms.ModelForm):
    """Form edit data pegawai (tanpa User ID)"""

    email = forms.EmailField(
        required=False,
        label="Email",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'contoh@email.com'
        })
    )

    tanggal_bergabung = forms.DateField(
        required=False,
        label="Tanggal Bergabung",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    tanggal_nonaktif = forms.DateField(
        required=False,
        label="Tanggal Non-Aktif",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    class Meta:
        model = Pegawai
        fields = [
            'nama_lengkap', 'email', 'nomor_hp', 'alamat', 'tanggal_lahir',
            'departemen', 'jabatan', 'cabang', 'mesin', 
            'mode_jam_kerja',
            'tanggal_bergabung', 'tanggal_nonaktif', 'is_shift_worker', 'is_active',
        ]
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'tanggal_lahir': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'nomor_hp': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'departemen': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'jabatan': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'cabang': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'mesin': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'mode_jam_kerja': forms.Select(attrs={
                'class': 'form-control select2'
            }),
            'is_shift_worker': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


# ==============================================================================
# FORMS - ABSENSI & LAPORAN
# Form untuk input absensi manual dan filter laporan
# ==============================================================================

class AbsensiAdminForm(forms.ModelForm):
    """Form input absensi manual oleh admin"""

    class Meta:
        model = Absensi
        fields = [
            'pegawai', 'tanggal', 'status', 
            'tap_masuk', 'tap_pulang',
            'tap_istirahat_keluar', 'tap_istirahat_masuk',
            'keterangan'
        ]
        widgets = {
            'pegawai': forms.Select(attrs={
                'class': 'form-control select2',
                'required': 'required'
            }),
            'tanggal': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': 'required'
            }),
            'status': forms.Select(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'tap_masuk': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_tap_masuk'
            }),
            'tap_pulang': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_tap_pulang'
            }),
            'tap_istirahat_keluar': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_tap_istirahat_keluar'
            }),
            'tap_istirahat_masuk': forms.TimeInput(attrs={
                'class': 'form-control',
                'type': 'time',
                'id': 'id_tap_istirahat_masuk'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Keterangan (opsional)'
            })
        }
        labels = {
            'pegawai': 'Pegawai',
            'tanggal': 'Tanggal',
            'status': 'Status',
            'tap_masuk': 'Jam Masuk',
            'tap_pulang': 'Jam Pulang',
            'tap_istirahat_keluar': 'Jam Istirahat Keluar',
            'tap_istirahat_masuk': 'Jam Istirahat Masuk',
            'keterangan': 'Keterangan'
        }


class LaporanFilterForm(forms.Form):
    """Form filter laporan absensi berdasarkan periode"""

    tanggal_mulai = forms.DateField(
        required=False,
        label="Tanggal Mulai",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    tanggal_akhir = forms.DateField(
        required=False,
        label="Tanggal Akhir",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )

    search_employee = forms.CharField(
        max_length=100,
        required=False,
        label="Cari Pegawai",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari nama atau User ID Pegawai...'
        })
    )


class PegawaiSearchForm(forms.Form):
    """Form pencarian cepat pegawai"""

    search_query = forms.CharField(
        max_length=100,
        required=False,
        label="Cari Pegawai",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Cari User ID, Nama, Jabatan, atau Departemen...'
        })
    )


# ==============================================================================
# FORMS - MASTER DATA
# Form untuk kelola master data: departemen, jabatan, cabang, mesin
# ==============================================================================

class MasterDepartemenForm(forms.ModelForm):
    """Form untuk master departemen"""

    class Meta:
        model = MasterDepartemen
        fields = ['nama', 'id_departemen', 'keterangan', 'is_active']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Information Technology',
                'required': 'required'
            }),
            'id_departemen': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: 01, 1234, 99',
                'maxlength': '5',
                'required': 'required',
                'pattern': '[0-9]+',
                'title': 'ID Departemen hanya boleh berisi angka'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }

    def clean_id_departemen(self):
        """Validasi id_departemen: wajib diisi, hanya angka, dan unik"""
        id_dept = self.cleaned_data.get('id_departemen', '').strip()

        if not id_dept:
            raise forms.ValidationError('ID departemen wajib diisi!')

        if not id_dept.isdigit():
            raise forms.ValidationError(
                'ID departemen hanya boleh berisi angka (0-9). Contoh: 01, 1234, 99'
            )

        # Cek duplikat (kecuali untuk update)
        qs = MasterDepartemen.objects.filter(id_departemen=id_dept)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)

        if qs.exists():
            raise forms.ValidationError(f'ID departemen {id_dept} sudah digunakan!')

        return id_dept


class MasterJabatanForm(forms.ModelForm):
    """Form untuk master jabatan"""

    class Meta:
        model = MasterJabatan
        fields = ['nama', 'kode', 'keterangan', 'is_active']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: Manager, Supervisor',
                'required': 'required'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contoh: MGR, SPV',
                'required': 'required'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Keterangan opsional'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MasterCabangForm(forms.ModelForm):
    """Form untuk master cabang"""

    class Meta:
        model = MasterCabang
        fields = ['nama', 'kode', 'alamat', 'ip_mesin_fingerprint', 'port_mesin', 'is_active']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'alamat': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'ip_mesin_fingerprint': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2
            }),
            'port_mesin': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': '4370'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }


class MasterMesinForm(forms.ModelForm):
    """Form untuk master mesin fingerprint"""

    class Meta:
        model = MasterMesin
        fields = ['nama', 'kode', 'ip_address', 'port', 'cabang', 'lokasi', 'keterangan', 'is_active']
        widgets = {
            'nama': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'kode': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'ip_address': forms.TextInput(attrs={
                'class': 'form-control',
                'required': 'required'
            }),
            'port': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': '4370'
            }),
            'cabang': forms.Select(attrs={
                'class': 'form-control select2',
                'required': 'required'
            }),
            'lokasi': forms.TextInput(attrs={
                'class': 'form-control'
            }),
            'keterangan': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
        }