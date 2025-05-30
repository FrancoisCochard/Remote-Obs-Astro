# Comprendre le pb USB de la station météo

05/11/2023 : la station météo est à l'arrêt après quelques jours de fonctionnement. Je fais quelques manipes pour comprendre ce qui se passe.

Symptôme : le vent et la pluie marchent toujours, mais pas le module météo :

![Capture d’écran du 2023-11-05 11-46-38](/home/observatoire/Téléchargements/Capture d’écran du 2023-11-05 11-46-38.png)

Quelques commandes :

```observatory@ubuntu:~$ df -h
observatory@ubuntu:~$ df -h
Filesystem      Size  Used Avail Use% Mounted on
tmpfs            91M  3,4M   88M   4% /run
/dev/mmcblk0p2   29G  8,9G   19G  32% /
tmpfs           453M     0  453M   0% /dev/shm
tmpfs           5,0M     0  5,0M   0% /run/lock
/dev/mmcblk0p1  253M  148M  105M  59% /boot/firmware
tmpfs            91M  4,0K   91M   1% /run/user/1000
```

```
observatory@ubuntu:~$ uptime
 10:27:30 up 4 days, 18:17,  1 user,  load average: 1,74, 1,60, 1,54
```

```
observatory@ubuntu:~$ lsusb
Bus 001 Device 004: ID 2e8a:000a Raspberry Pi Pico
Bus 001 Device 006: ID 0403:6001 Future Technology Devices International, Ltd FT232 Serial (UART) IC
Bus 001 Device 005: ID 0781:558a SanDisk Corp. Ultra
Bus 001 Device 007: ID 0424:7800 Microchip Technology, Inc. (formerly SMSC) 
Bus 001 Device 003: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 002: ID 0424:2514 Microchip Technology, Inc. (formerly SMSC) USB 2.0 Hub
Bus 001 Device 001: ID 1d6b:0002 Linux Foundation 2.0 root hub
```

Je constate que la clé USB est bien là, mais n'est pas montée.

Il semble que les 3 connecteurs USB sont bien là : clé USB (SanDisk), module météo (Pico) et capteur de vente (FT232 UART). Bigre.

Weather.service tourne bien. Idem pour shelter.service, et power.service et dashboard.service

```
observatory@ubuntu:~$ ls -l /dev/tty[A,U]*
crw-rw---- 1 root dialout 166,  0 oct.  31 16:13 /dev/ttyACM0
crw-rw---- 1 root dialout 204, 64 oct.  31 16:13 /dev/ttyAMA0
crw-rw---- 1 root dialout 188,  0 oct.  31 16:10 /dev/ttyUSB0
```

Petite manipe : j'arrête le service weather (systemctl stop weather.service), puis j'écoute avec Minicom le port /dev/ttyACM0:

```
observatory@ubuntu:~$ minicom -D /dev/ttyACM0

Bienvenue dans minicom 2.8                                                                                                               
OPTIONS: I18n                                                                                                                            
Port /dev/ttyACM0                                                                                                                         
Tapez CTRL-A Z pour voir l'aide concernant les touches spéciales                                                                         
$SKERR,5,5,4*45                                                                                                                   $SKTPH,inf,inf,inf*19                                                                                                             $SKIRT,6.1,5.2*57                                                                                                                 $SKLUM,2.609*43                                                                                                                   $SKERR,5,5,0*41                                                                                                                   $SKTPH,inf,inf,inf*19                                                                                                             $SKIRT,6.1,5.4*51                                                                                                                 $SKLUM,2.754*4A                                                                                                                   $SKERR,5,5,1*40                                                                                                                   $SKTPH,inf,inf,inf*19                                                                                                             $SKIRT,6.1,5.3*56                                                                                                                 $SKLUM,2.305*4A                                                                                                                   $SKERR,5,5,2*43
$SKTPH,inf,inf,inf*19
$SKIRT,6.1,5.2*57
$SKLUM,2.885*49
$SKERR,5,5,3*42
$SKTPH,inf,inf,inf*19
```

Je vois bien des trames... mais visiblement il y a une erreur (valeurs infinies, et chaine SKERR) !

> Cette fois, c'est peut-être bien le module météo qui est en panne ?

Si j'écoute avec Minicom sur les deux autres ports USB (ttyAMA0 et ttyUSB0), je n'ai rien (avec les mêmes paramètres).

Je reboote (sudo shutdown -r now)... et ça retombe en marche !

Fin de la manipe - 05 /11/2023

## Nouveau plantage le 29/11/2023

- lsusb : je ne vois plus le Pico.
- Alors je fais un reboot (sudo shutdown -r now)
- A ce stade, je ne sais pas si c'est le Pico qui n'émet plus (module météo) ou si c'est le port USB qui est désactivé.
- Le reboot a pris un temps très long (10 minutes ?). Pendant un moment il me disait que les user sans privilège doivent attendre un peu pour se logger (systèe en train de booter). Je n'ai jamais vu ça.
- Mais après le reboot, tout retombe en marche, je vois de nouveau le Pico dans un lsusb.