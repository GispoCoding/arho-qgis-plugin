# Validering (Validointi)

Via knappen *Validointi* kommer du till valideringspanelen, där du kan validera planen genom att trycka på ***Validoi kaavasuunnitelma***. Valideringen kontrollerar om planen följer definitionerna i Ryhtis plandatamodell. Med tanke på arbetsflödet kan det vara förnuftigt att validera planen ganska ofta – på så sätt är det lättast att spåra eventuella valideringsfel.

Valideringens felmeddelanden kommer via Sykes gränssnitt. För att underlätta tolkningen och lokaliseringen av felen har en del funktioner implementerats i Arho:

- Gispo har lagt till en beskrivning (*Kuvaus*) i meddelandet, vilken kan hittas i Sykes valideringsdokument.
- Du ser felmeddelandet i sin helhet när du för muspekaren över felet.
- Genom att trycka en gång på felmeddelandet blinkar det felaktiga objektet med rött på kartan.
- Genom att dubbelklicka på felmeddelandet öppnas objektets uppgifter, och du kan åtgärda felet genom att redigera informationen.

![Panelen ”Validointi” med ett valideringsfel för planen och dess verktygstips med felkod](images/validation-1.png)

Information om Ryhtis valideringsregler finns på [Miljöcentralens webbplats](https://ryhti.syke.fi/alueidenkaytto/tietomallimuotoinen-kaavoitus/kaavasuunnitelman-validointisaannot/). Det lönar sig även att bekanta sig med dokumentet [Kaavatiedon-validointisaannot-ja-paluuarvot.pdf](https://ryhti.syke.fi/wp-content/uploads/sites/2/2023/11/Kaavatiedon-validointisaannot-ja-paluuarvot.pdf). Till exempel kan valideringsfelet `lifecycle__req_dateonly_incorrect_type, The date must be in the format yyyy-mm-dd` också innebära att ett obligatoriskt datum saknas helt.
