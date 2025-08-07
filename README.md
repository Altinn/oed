# oed
Oppgjør etter dødsfall

Lyseblå betyr at Digitalt Dødsbo teamet er ansvarlig for tjenesten.

```mermaid
flowchart TB
    %% 👤 User
    User@{ img: "https://raw.githubusercontent.com/FortAwesome/Font-Awesome/refs/heads/7.x/svgs/regular/user.svg", pos: "b", label: "Bruker", w: 60, h: 60, constraint: "on" }

    %% Altinn 2
    subgraph Altinn2 [Altinn 2]
        A2Correspondance[Altinn 2 Korrespondanse]
    end
    
    %% DAN (data.altinn.no)
    subgraph DAN ["DAN (data.altinn.no)"]
        BankKf["🔗 Bits - 'Kundeforhold'"]
        BankKd["🔗 Bits - 'Kontodetaljer'"]
        BankKt["🔗 Bits - 'Kontotransaksjoner'"]
        SVV["🔗 SVV - 'Kjoretoy'"]
        Kartverket["🔗 Kartverket - 'Grunnbok'"]
        NorskPensjon["🔗 Norsk pensjon - 'NorskPensjon'"]
        MarriagePact["🔗 Løsøreregisteret - 'Ektepakt'"]
        Frreg["🔗 Folkeregisteret - 'FregPerson'"]
        click BankKf "https://github.com/data-altinn-no/plugin-banking/blob/main/src/Altinn.Dan.Plugin.Banking/Plugin.cs#L61" "Gå til Github - Kundeforhold" _blank
        click BankKd "https://github.com/data-altinn-no/plugin-banking/blob/main/src/Altinn.Dan.Plugin.Banking/Plugin.cs#L79" "Gå til Github - Kontodetaljer" _blank
        click BankKt "https://github.com/data-altinn-no/plugin-banking/blob/main/src/Altinn.Dan.Plugin.Banking/Plugin.cs#L70" "Gå til Github - Kontotransaksjoner" _blank
        click SVV "https://github.com/data-altinn-no/plugin-statensvegvesen" "Gå til Github - SVV" _blank
        click Kartverket "https://github.com/data-altinn-no/plugin-kartverket" "Gå til Github - Kartverket" _blank
        click MarriagePact "https://github.com/data-altinn-no/plugin-brreg/blob/main/src/Dan.Plugin.Brreg/Ektepakt.cs#L66" "Gå til Github - Ektepakt" _blank
        click NorskPensjon "https://github.com/data-altinn-no/plugin-pensjon" "Gå til Github - Norskpensjon" _blank
        click Frreg "https://github.com/data-altinn-no/plugin-skatteetaten/blob/main/src/Dan.Plugin.Skatteetaten/Freg.cs#L97" "Gå til Github - Folkeregisteret" _blank

        BankKf ~~~ BankKd
        BankKt ~~~ SVV
        Kartverket ~~~ NorskPensjon
        MarriagePact ~~~ Frreg
    end

    %% Digitalt Dødsbo
    subgraph DD[Digitalt Dødsbo]
        TestApp[🔗 Testdata]
        E2E[🔗 E2E test]
        DDInfra[🔗 DD Infra]
        Msging[🔗 Korrespondanse bibliotek]
        MetaDb[(Metadata database)]
        DDAuthz[🔗 DD Authz]
        TaskQ[(TaskQueue)]
        Feedpoller[🔗 Feedpoller og proxy]
        AdminApp[🔗 Admin]
        click TestApp "https://github.com/Altinn/oed-testdata-app" "Gå til Github - Testdata" _blank
        click E2E "https://github.com/altinn/dd-e2e-test/" "Gå til Github - E2E" _blank
        click DDInfra "https://github.com/Altinn/dd-infrastructure/" "Gå til Github - Infrastruktur" _blank
        click DDAuthz "https://github.com/Altinn/oed-authz" "Gå til Github - A3Authz" _blank
        click Feedpoller "https://github.com/Altinn/oed-feedpoller" "Gå til Github - Feedpoller" _blank
        click Msging "https://github.com/Altinn/oed-messaging" "Gå til Github - Korrespondanse bibliotek" _blank
        click AdminApp "https://github.com/Altinn/oed-admin" "Gå til Github - Admin" _blank

        TestApp ~~~ E2E ~~~ DDInfra ~~~ Msging
        MetaDb ~~~ DDAuthz
        MetaDb ~~~ TaskQ
        DDAuthz ~~~ Feedpoller
        AdminApp-->MetaDb
    end

    %% Altinn 3
    subgraph Altinn3 [Altinn 3]
        A3Authz[🔗 Altinn Autorisasjon]
        A3Events[🔗 Altinn 3 Event systemet]
        Inbox[Innboks]
        AltinnMsg[Altinn Melding]
        Estate[🔗 Oppgjør etter dødsfall]
        DDEvents[🔗 oed-events]
        Declaration[🔗 Skifteerklæring]
        click A3Authz "https://github.com/Altinn/altinn-authorization" "Gå til Github - Altinn autorisasjon" _blank
        click A3Events "https://github.com/Altinn/altinn-events" "Gå til Github - Altinn Events" _blank
        click Estate "https://altinn.studio/repos/digdir/oed" "Gå til Gitea - Digitalt Dødsbo" _blank
        click Declaration "https://altinn.studio/repos/digdir/oed-declaration" "Gå til Gitea - Skifteerklæring" _blank
        click DDEvents "https://altinn.studio/repos/digdir/oed-events" "Gå til Gitea - Events" _blank
    end

    %% Domstol administrasjonen
    subgraph DA [Domstol administrasjonen]
        DAFeed[Hendelseslista]
        DA_Node[Domstol Administrasjonen]
    end

    Altinn2 ~~~ DAN
    %% Flow
    User -- Logger inn --> A3Authz --> Inbox --> AltinnMsg --> Estate
    Estate --> TaskQ
    Estate -- Autoriserer bruker --> A3Authz
    A3Authz & Estate -- Henter roller --> DDAuthz
    DDEvents -- Publiser CloudEvents --> A3Events
    Estate --> Declaration -- Publiser app-event --> A3Events
    DA_Node -- Henter skifteerklæring --> Estate
    A3Events --> DA_Node

    Feedpoller -- Poll hvert 5. minutt --> DDEvents
    DDEvents -- Henter hendelsesliste --> DAFeed
    A3Events <--> Estate --> MetaDb
    TaskQ -- Send korrespondanse --> A2Correspondance --> User
    Estate --> DAN

    %%  Clickable links
   

    %% 🎨 Styles
    classDef altinn3 fill:#4b5563,stroke:#95acc9,stroke-width:2px,color:#fff;
    classDef dd fill:#025fa6,stroke:##b0d8f7,stroke-width:2px,color:#fff;
    classDef da fill:#4b5563,stroke:#95acc9,stroke-width:2px,color:#fff;
    classDef arkiv fill:#065f46,stroke:#34d399,stroke-width:2px,color:#fff;
    classDef user fill:#fff;
    classDef dan fill:#4b5563,stroke:#95acc9,stroke-width:2px,color:#fff;
    classDef sg fill:#;

    class Altinn2,Altinn3 sg

    class Altinn,Inbox,A3Events,A3Authz,AltinnMsg,A2Correspondance altinn3
    class Estate,TaskQ,Declaration,DDEvents,Feedpoller,DDAuthz,AdminApp,MetaDb,TestApp,E2E,DDInfra,Msging dd
    class DA_Node,DAFeed da
    class ArchiveSystem arkiv
    class User user
    class BankKf,BankKd,BankKt,SVV,Kartverket,NorskPensjon,MarriagePact,Frreg dan
```