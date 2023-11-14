# FILTRE VELOCITE YAMAHA REFACE CP 

Install
----
- Modules python : mido, python-rtmidi (et non rtmidi)
- (OBSOLETE) Le "local control" doit être à OFF et "midi control" à ON : voir manuels.
- S'assurer que /home/pi/startup.sh est exécutable
- Ajouter `su -c /home/pi/startup.sh pi &` dans `rc.local`


Doc
----
Specs MIDI Reface : https://jp.yamaha.com/files/download/other_assets/7/794817/reface_en_dl_b0.pdf
Doc Mido : https://readthedocs.org/projects/mido/downloads/pdf/latest/
Manuel Reface CS :  https://www.manualslib.com/manual/959024/Yamaha-Reface-Cs.html?page=47#manual
Manuel Reface : https://aadl.org/files/catalog_guides/1508075_reface_manual.pdf

Option :
https://www.yamahasynth.com/learn/reface/reface-cp-midi-primer-setting-midi-receive-channel
