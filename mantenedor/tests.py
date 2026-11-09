from datetime import date

from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from .models import Calificacion


class PermisosTest(TestCase):
    def setUp(self):
        self.lector = User.objects.create_user('lector', password='clave1234')
        self.staff = User.objects.create_user(
            'jefe', password='clave1234', is_staff=True
        )
        self.admin_grupo = User.objects.create_user('admin2', password='clave1234')
        self.admin_grupo.groups.add(
            Group.objects.create(name='Administradores')
        )
        self.cal = Calificacion.objects.create(
            ejercicio=2024, mercado='CFI', instrumento='ABC',
            fecha_pago=date(2024, 1, 1), secuencia=1, origen='BOLSA',
        )

    def test_sin_login_redirige_al_login(self):
        r = self.client.get(reverse('inicio'))
        self.assertRedirects(r, '/login/?next=/')

    def test_lector_puede_ver_listado(self):
        self.client.login(username='lector', password='clave1234')
        self.assertEqual(self.client.get(reverse('inicio')).status_code, 200)

    def test_lector_recibe_403_al_crear_editar_eliminar(self):
        self.client.login(username='lector', password='clave1234')
        self.assertEqual(self.client.get(reverse('crear')).status_code, 403)
        self.assertEqual(
            self.client.get(reverse('editar', args=[self.cal.pk])).status_code, 403
        )
        r = self.client.post(reverse('eliminar', args=[self.cal.pk]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Calificacion.objects.filter(pk=self.cal.pk).exists())

    def test_staff_y_grupo_pueden_modificar(self):
        for usuario in ('jefe', 'admin2'):
            self.client.login(username=usuario, password='clave1234')
            self.assertEqual(self.client.get(reverse('crear')).status_code, 200)
            self.client.logout()
