# Ibruktagande

Den här sidan beskriver hur en organisation tar Arho i bruk. Om du är användare av Arho och bara vill komma igång, läs sidan [Ibruktagande](../manual/setup.md) i användarmanualen.

## Vad du behöver { #requirements }

- **QGIS**, helst LTR-versionen
- **Insticksprogrammet Arho**
- **Arhos QGIS-projektfil**
- **bakgrundssystemet**, där plandata sparas och som sköter förbindelserna till Ryhti

Delarna beskrivs närmare på sidan [Om Arho](index.md#parts).

## Insticksprogrammet { #plugin }

Insticksprogrammet Arho installeras från GitHub som ett experimentellt insticksprogram. Instruktionen finns på sidan [Ibruktagande](../manual/setup.md#install) i användarmanualen.

## Bakgrundssystemet { #backend }

Bakgrundssystemets källkod finns i repositoriet [arho-backend](https://github.com/GispoCoding/arho-backend). Bakgrundssystemet körs i molntjänsten AWS och installeras med Terraform. Installationsanvisningen finns i filen [infra/README.md](https://github.com/GispoCoding/arho-backend/blob/main/infra/README.md) i repositoriet.

## Hjälp med ibruktagandet { #help }

Gispo erbjuder Arho också som tjänst: drift, ibruktagande och support. Mer information finns på [gispo.fi/arho](https://www.gispo.fi/arho).

## Manualer { #guides }

- **Användare**: börja med sidan [Ibruktagande](../manual/setup.md) i användarmanualen.
- **Huvudanvändare**: de tekniska stegen för ibruktagandet och huvudanvändarens uppgifter finns i en separat manual (på finska): [Arho tekninen ohje – käyttöönotto ja pääkäyttäjä](https://docs.google.com/document/d/1HaIzgdJiOIgSZ1bA6tcsnur_4W45OwxJv8bEWOxZIeM/edit?usp=sharing).
