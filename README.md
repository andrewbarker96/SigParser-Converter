# SigParser to Ring Central Conversion

## Usage

My company recently made the switch to Ring Central from an on Prem VOIP system. Late last year, my company turned to <a href="https://sigparser.com/">"SigParser"</a> as an alternative to better managing our contacts. Prior to this we stored our 20,000+ contacts in our Exchange server, it got to be too bloated and so we looked for alternate solutions. SigParser is great as it automatically updates contacts based on email signatures. Making it more efficient to keep an updated contact system.

Now that we are moving to Ring Central, we have wanted to find a way to best convert our ever changing SigParser contacts into our Ring Central contact library. Due to SigParser's unique table header's, we needed to find a way to appropriately change SigParser's data to match RingCentral's accepted import methods. By exporting our library of contacts from SigParser and renaming to watch this script, we are able to make the necessary changes to fit Ring Central's recommended layout. We can then import our Filtered Contacts file and keep a steady update of all our contacts. Eliminating the need for one or two individuals to constantly spend hours combing through old contacts.

### SigParser Exported Headers

["Contact Status", "Full Name", "Company Name", "First Name", "Last Name", "Job Title", "Email Address", "Office Phone", "Home Phone", "Direct Phone", "Mobile Phone", "Fax Phone", "SigParser Contact ID"]

"Contact Status", "Full Name", "Company Name" are locked and cannot be updated via SigParser thus the need for larger data entries. We slim this down via the converter.py script. We also then can save these data columns for later should we have need to utilize them.

### Why not utilize an API?

We would love to be able to utilize an API to better update and maintain our contact system through ring central. However the API costs are too great, thus this allows us to still be efficient in maintaining our contacts without spending large sums of money.
