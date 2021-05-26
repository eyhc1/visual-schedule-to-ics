# Visual Schedule to ics
 Export your UW Class Schedule to an ics file that you could import into your calendar app such as Google Calendar or Outlook
## Use
 <s>You can either run the run.bat file</s>, for the latest version, you can just run the sample `ClassConverter.exe` (Windows only) or if you can just edit `UWclasses_beta.py` and run it from there.
## Requires
- BeautifulSoup
- requests
## Known Issues
 - You can't use Shadowsock or similar survices while running the program due (maybe) to SSL issues (the sample program can though)
 - program will load infinitely if you run with `getpass()` in PyCharm as you type in your passwords
 - <s>program do not work for in-person classes</s>
## TODO:
- [ ] Fix Issues
- [X] Make support for in-person classes
- [ ] parse building location from campus map to the ics file
- [ ] Convert final exam schedule as well
- [ ] reduce redundancy
