# Generated migration - FIXED VERSION
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        ('absensi_app', '0012_pegawaimodeassignment'),
    ]

    operations = [
        # ✅ STEP 1: TAMBAH field group_name DULU (sebelum AlterUniqueTogether)
        migrations.AddField(
            model_name='modejamkerjajadwal',
            name='group_name',
            field=models.CharField(default='Default Group', help_text='Contoh: Shift Pagi, Shift Siang, Shift Office', max_length=100, verbose_name='Nama Grup Jam Kerja'),
            preserve_default=False,
        ),

        # ✅ STEP 2: Migrate data dari nama_shift ke group_name (gunakan nama tabel yang ada)
        migrations.RunSQL(
            sql="UPDATE mode_jam_kerja_jadwal SET group_name = COALESCE(nama_shift, 'Default Group');",
            reverse_sql="UPDATE mode_jam_kerja_jadwal SET group_name = 'Default Group';",
        ),

        # ✅ STEP 3: HAPUS duplikat (gunakan nama tabel yang ada)
        migrations.RunSQL(
            sql="""
            DELETE FROM mode_jam_kerja_jadwal
            WHERE id NOT IN (
                SELECT MAX(id) FROM mode_jam_kerja_jadwal
                GROUP BY mode_id, group_name, hari
            );
            """,
            reverse_sql="",
        ),

        # ✅ STEP 4: TAMBAH field ke Pegawai
        migrations.AddField(
            model_name='pegawai',
            name='jam_kerja_assignment',
            field=models.JSONField(blank=True, default=dict, help_text='Format: {"0": "Shift Pagi", "1": "Shift Siang", ...}'),
        ),

        # ✅ STEP 5: Alter field pegawai.mode_jam_kerja
        migrations.AlterField(
            model_name='pegawai',
            name='mode_jam_kerja',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='pegawai_list', to='absensi_app.mastermodejamkerja'),
        ),

        # ✅ STEP 6: Remove index lama
        migrations.RemoveIndex(
            model_name='modejamkerjajadwal',
            name='mode_jam_ke_mode_id_d63071_idx',
        ),

        # ✅ STEP 7: Change Meta options
        migrations.AlterModelOptions(
            name='modejamkerjajadwal',
            options={'ordering': ['mode', 'group_name', 'hari', 'urutan'], 'verbose_name': 'Jadwal Mode Jam Kerja', 'verbose_name_plural': 'Jadwal Mode Jam Kerja'},
        ),

        # ✅ STEP 8: Alter unique_together (SEKARANG group_name SUDAH ADA)
        migrations.AlterUniqueTogether(
            name='modejamkerjajadwal',
            unique_together={('mode', 'group_name', 'hari')},
        ),

        # ✅ STEP 9: Add index baru
        migrations.AddIndex(
            model_name='modejamkerjajadwal',
            index=models.Index(fields=['mode', 'group_name', 'hari'], name='mode_jam_ke_mode_id_ad8dd8_idx'),
        ),

        # ✅ STEP 10: HAPUS fields lama (TERAKHIR)
        # NOTE: departemen_id tidak ada, yang ada di DB adalah departemen (FK)
        # Jadi kita hanya hapus fields yang benar-benar ada
        migrations.RemoveField(
            model_name='modejamkerjajadwal',
            name='is_hari_kerja',
        ),
        migrations.RemoveField(
            model_name='modejamkerjajadwal',
            name='nama_shift',
        ),
    ]