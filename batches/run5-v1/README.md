# Run 5 provisional signal records

171 unclassified transit-like signal dossiers from 229 imported records. Each contains saved
photometry, covariance, robustness, timing and signed alternative diagnostics. Source, timing,
physical scenario, noise coverage and survey reliability remain unresolved. These are
preliminary evidence records; no planet or discovery-priority claim is made.

Fresh configured Exoplanet MCP checks on 2026-10-11 used the adopted diagnostic ephemerides,
300-arcsecond cones and recorded period/harmonic criteria. All 229 calls succeeded: 220 indexed
nonmatches and nine match hypotheses. Earlier dated direct screens cover ExoFOP TOI/CTOI,
MAST EB and the TESS Ten Thousand EB catalogue. Their [snapshots](catalogue-snapshots.json)
retain table coverage, parsing failures and limits. Six invalid catalogue rows prevent a
completeness claim; literature and proper-motion/host reconciliation remain open.

The [complete outcome ledger](outcomes.json) conserves every imported record:

| Route | Records |
|---|---:|
| Provisional no-match signal record | 171 |
| Prior-report or catalog-match hypothesis | 13 |
| No adopted diagnostic ephemeris | 29 |
| Nonpositive or unavailable baseline dip | 3 |
| Insufficient usable multisector evidence | 7 |
| Dip not positive in all sector leaveouts | 6 |
| **Total** | **229** |

The record-selection rule is disclosed in [the batch workflow](../../docs/batch-publication.md).
It selects positive saved dips under both baseline orders, usable events in at least two
sectors and positive sector-leaveout depths. It is not a calibrated detection threshold.
27 dossiers have the saved odd/even diagnostic flag and explicitly identify the possible
binary explanation. Other secondary, harmonic, baseline, coverage and fit anomalies remain
in each dossier; absence of an odd/even flag does not establish a planet.

All records provide **evidence inspection only**. Their manifest hashes verify exported bytes;
there is no end-to-end public numerical rerun certificate or DOI. This batch does not claim
that every record is novel, or that all 222 original coarse catalog nonmatches were discoveries.

| Aperture TIC / signal | Diagnostic period (d) | Conditional depth (ppm) | Odd/even diagnostic |
|---|---:|---:|---|
| [101909456 / S01](../../candidates/tic-101909456-s01/README.md) | 1.75807705 | 888.2 | no recorded flag |
| [106146535 / S01](../../candidates/tic-106146535-s01/README.md) | 1.09704207 | 625.3 | no recorded flag |
| [117942905 / S01](../../candidates/tic-117942905-s01/README.md) | 0.42673903 | 1251.4 | flagged |
| [119870339 / S01](../../candidates/tic-119870339-s01/README.md) | 0.81981963 | 2083.4 | no recorded flag |
| [119926654 / S01](../../candidates/tic-119926654-s01/README.md) | 1.45906808 | 3821.4 | flagged |
| [120660805 / S01](../../candidates/tic-120660805-s01/README.md) | 2.17335537 | 3298.3 | no recorded flag |
| [124257344 / S01](../../candidates/tic-124257344-s01/README.md) | 1.01792968 | 1366.7 | no recorded flag |
| [128833851 / S01](../../candidates/tic-128833851-s01/README.md) | 4.05074922 | 2973.9 | no recorded flag |
| [132066001 / S01](../../candidates/tic-132066001-s01/README.md) | 0.97838182 | 2656.7 | no recorded flag |
| [134412679 / S01](../../candidates/tic-134412679-s01/README.md) | 2.62818094 | 1427.0 | no recorded flag |
| [135315597 / S01](../../candidates/tic-135315597-s01/README.md) | 5.16314746 | 1865.8 | no recorded flag |
| [140175607 / S01](../../candidates/tic-140175607-s01/README.md) | 0.69135013 | 6620.5 | flagged |
| [141939616 / S01](../../candidates/tic-141939616-s01/README.md) | 11.74540477 | 4085.0 | no recorded flag |
| [144003599 / S01](../../candidates/tic-144003599-s01/README.md) | 1.07611322 | 2223.8 | no recorded flag |
| [146998411 / S01](../../candidates/tic-146998411-s01/README.md) | 1.68838625 | 1648.9 | no recorded flag |
| [147024543 / S01](../../candidates/tic-147024543-s01/README.md) | 2.79668892 | 1479.1 | no recorded flag |
| [151437417 / S01](../../candidates/tic-151437417-s01/README.md) | 0.87033091 | 21185.9 | flagged |
| [158159741 / S01](../../candidates/tic-158159741-s01/README.md) | 1.80689752 | 1533.7 | no recorded flag |
| [158620278 / S01](../../candidates/tic-158620278-s01/README.md) | 13.47534119 | 504.4 | no recorded flag |
| [158712138 / S01](../../candidates/tic-158712138-s01/README.md) | 2.69721019 | 2341.6 | no recorded flag |
| [161357250 / S01](../../candidates/tic-161357250-s01/README.md) | 4.92272145 | 1456.9 | no recorded flag |
| [162620520 / S01](../../candidates/tic-162620520-s01/README.md) | 3.41287730 | 2079.5 | flagged |
| [163031959 / S01](../../candidates/tic-163031959-s01/README.md) | 1.54691113 | 665.9 | no recorded flag |
| [1688320944 / S01](../../candidates/tic-1688320944-s01/README.md) | 12.33111187 | 1971.7 | no recorded flag |
| [172943975 / S01](../../candidates/tic-172943975-s01/README.md) | 4.03168546 | 4438.4 | no recorded flag |
| [178361782 / S01](../../candidates/tic-178361782-s01/README.md) | 6.10646734 | 1899.4 | no recorded flag |
| [188129917 / S01](../../candidates/tic-188129917-s01/README.md) | 3.25787118 | 7537.7 | no recorded flag |
| [189339098 / S01](../../candidates/tic-189339098-s01/README.md) | 1.35180817 | 3730.0 | no recorded flag |
| [189439662 / S01](../../candidates/tic-189439662-s01/README.md) | 1.65037675 | 7568.9 | no recorded flag |
| [19899732 / S01](../../candidates/tic-19899732-s01/README.md) | 0.64343548 | 9760.6 | flagged |
| [207520598 / S01](../../candidates/tic-207520598-s01/README.md) | 7.59581821 | 1266.0 | no recorded flag |
| [208432222 / S01](../../candidates/tic-208432222-s01/README.md) | 5.86014120 | 20531.9 | flagged |
| [208666173 / S01](../../candidates/tic-208666173-s01/README.md) | 1.14714379 | 4488.0 | no recorded flag |
| [215091718 / S01](../../candidates/tic-215091718-s01/README.md) | 3.78273888 | 2218.2 | no recorded flag |
| [216669784 / S01](../../candidates/tic-216669784-s01/README.md) | 1.20129260 | 1386.4 | no recorded flag |
| [21694454 / S01](../../candidates/tic-21694454-s01/README.md) | 1.80974370 | 56516.4 | no recorded flag |
| [219382845 / S01](../../candidates/tic-219382845-s01/README.md) | 1.11766988 | 2303.3 | no recorded flag |
| [219452141 / S01](../../candidates/tic-219452141-s01/README.md) | 1.39594665 | 2038.4 | no recorded flag |
| [221425588 / S01](../../candidates/tic-221425588-s01/README.md) | 1.24053019 | 3762.4 | no recorded flag |
| [222224160 / S01](../../candidates/tic-222224160-s01/README.md) | 1.63921964 | 2547.2 | no recorded flag |
| [23205275 / S01](../../candidates/tic-23205275-s01/README.md) | 1.85886421 | 7102.3 | no recorded flag |
| [23205280 / S01](../../candidates/tic-23205280-s01/README.md) | 1.85886380 | 14567.9 | no recorded flag |
| [243500407 / S01](../../candidates/tic-243500407-s01/README.md) | 0.68639664 | 1179.2 | no recorded flag |
| [245101439 / S01](../../candidates/tic-245101439-s01/README.md) | 3.47727242 | 2391.3 | no recorded flag |
| [246469763 / S01](../../candidates/tic-246469763-s01/README.md) | 1.77059904 | 1742.8 | no recorded flag |
| [253145639 / S01](../../candidates/tic-253145639-s01/README.md) | 1.32935234 | 9935.0 | no recorded flag |
| [253347253 / S01](../../candidates/tic-253347253-s01/README.md) | 1.27712500 | 2798.2 | no recorded flag |
| [253384622 / S01](../../candidates/tic-253384622-s01/README.md) | 2.08705565 | 1012.8 | no recorded flag |
| [260569590 / S01](../../candidates/tic-260569590-s01/README.md) | 1.49506409 | 1543.6 | no recorded flag |
| [260841561 / S01](../../candidates/tic-260841561-s01/README.md) | 13.29079691 | 187.8 | no recorded flag |
| [261102618 / S01](../../candidates/tic-261102618-s01/README.md) | 2.93593065 | 1456.4 | no recorded flag |
| [261119502 / S01](../../candidates/tic-261119502-s01/README.md) | 11.75651312 | 1433.7 | no recorded flag |
| [265566507 / S01](../../candidates/tic-265566507-s01/README.md) | 12.98075736 | 558.4 | no recorded flag |
| [268187402 / S01](../../candidates/tic-268187402-s01/README.md) | 1.59290959 | 1279.8 | no recorded flag |
| [268201230 / S01](../../candidates/tic-268201230-s01/README.md) | 1.71398157 | 23466.9 | flagged |
| [271609681 / S01](../../candidates/tic-271609681-s01/README.md) | 2.74049950 | 856.8 | no recorded flag |
| [276645751 / S01](../../candidates/tic-276645751-s01/README.md) | 0.74768618 | 2044.6 | no recorded flag |
| [277514841 / S01](../../candidates/tic-277514841-s01/README.md) | 2.39138428 | 2201.0 | no recorded flag |
| [277962250 / S01](../../candidates/tic-277962250-s01/README.md) | 0.83212985 | 888.8 | no recorded flag |
| [281705082 / S01](../../candidates/tic-281705082-s01/README.md) | 1.45779611 | 2416.3 | flagged |
| [281779833 / S01](../../candidates/tic-281779833-s01/README.md) | 12.98501100 | 394.4 | no recorded flag |
| [282413282 / S01](../../candidates/tic-282413282-s01/README.md) | 3.44915412 | 7551.0 | no recorded flag |
| [2835596 / S01](../../candidates/tic-2835596-s01/README.md) | 1.60923180 | 1072.5 | flagged |
| [286763467 / S01](../../candidates/tic-286763467-s01/README.md) | 2.90251992 | 29125.6 | no recorded flag |
| [290342858 / S01](../../candidates/tic-290342858-s01/README.md) | 1.11379249 | 5845.9 | flagged |
| [292291978 / S01](../../candidates/tic-292291978-s01/README.md) | 11.48023544 | 2318.4 | flagged |
| [294235592 / S01](../../candidates/tic-294235592-s01/README.md) | 3.41602752 | 2597.0 | no recorded flag |
| [295376786 / S01](../../candidates/tic-295376786-s01/README.md) | 13.10187390 | 3834.9 | no recorded flag |
| [295478570 / S01](../../candidates/tic-295478570-s01/README.md) | 2.66538018 | 1459.6 | no recorded flag |
| [297093620 / S01](../../candidates/tic-297093620-s01/README.md) | 1.82467863 | 4143.7 | flagged |
| [298913278 / S01](../../candidates/tic-298913278-s01/README.md) | 2.91311744 | 1521.9 | no recorded flag |
| [303515275 / S01](../../candidates/tic-303515275-s01/README.md) | 0.85683334 | 1978.9 | no recorded flag |
| [304325119 / S01](../../candidates/tic-304325119-s01/README.md) | 0.97505027 | 351.2 | no recorded flag |
| [306043829 / S01](../../candidates/tic-306043829-s01/README.md) | 0.87076937 | 2787.9 | no recorded flag |
| [306460615 / S01](../../candidates/tic-306460615-s01/README.md) | 6.06426822 | 4040.9 | no recorded flag |
| [306915668 / S01](../../candidates/tic-306915668-s01/README.md) | 1.22003416 | 5540.3 | no recorded flag |
| [308337104 / S01](../../candidates/tic-308337104-s01/README.md) | 4.05477603 | 46509.2 | no recorded flag |
| [308841804 / S01](../../candidates/tic-308841804-s01/README.md) | 0.68723223 | 4466.1 | flagged |
| [311049477 / S01](../../candidates/tic-311049477-s01/README.md) | 1.40141842 | 1553.3 | no recorded flag |
| [313083329 / S01](../../candidates/tic-313083329-s01/README.md) | 1.21895296 | 2777.9 | no recorded flag |
| [320088883 / S01](../../candidates/tic-320088883-s01/README.md) | 2.30187434 | 2102.1 | flagged |
| [320176061 / S01](../../candidates/tic-320176061-s01/README.md) | 13.02497109 | 242.3 | no recorded flag |
| [32264593 / S01](../../candidates/tic-32264593-s01/README.md) | 2.99115226 | 1463.7 | no recorded flag |
| [322985701 / S01](../../candidates/tic-322985701-s01/README.md) | 0.92736526 | 3156.3 | no recorded flag |
| [325076080 / S01](../../candidates/tic-325076080-s01/README.md) | 10.81974967 | 222.4 | no recorded flag |
| [325732475 / S01](../../candidates/tic-325732475-s01/README.md) | 1.78060906 | 1158.6 | no recorded flag |
| [330721101 / S01](../../candidates/tic-330721101-s01/README.md) | 2.14260152 | 3279.0 | no recorded flag |
| [33152820 / S01](../../candidates/tic-33152820-s01/README.md) | 0.93418276 | 2896.5 | flagged |
| [331676454 / S01](../../candidates/tic-331676454-s01/README.md) | 0.70159131 | 422.6 | no recorded flag |
| [332275175 / S01](../../candidates/tic-332275175-s01/README.md) | 0.76840047 | 944.0 | no recorded flag |
| [333661705 / S01](../../candidates/tic-333661705-s01/README.md) | 1.38323732 | 766.5 | no recorded flag |
| [335209543 / S01](../../candidates/tic-335209543-s01/README.md) | 2.58331721 | 19236.8 | flagged |
| [335594325 / S01](../../candidates/tic-335594325-s01/README.md) | 1.96199624 | 2197.1 | no recorded flag |
| [337318278 / S01](../../candidates/tic-337318278-s01/README.md) | 3.67363419 | 441.8 | no recorded flag |
| [338402953 / S01](../../candidates/tic-338402953-s01/README.md) | 4.87132136 | 4775.7 | no recorded flag |
| [339211982 / S01](../../candidates/tic-339211982-s01/README.md) | 2.05111198 | 1927.3 | no recorded flag |
| [339451799 / S01](../../candidates/tic-339451799-s01/README.md) | 4.52576109 | 31755.6 | no recorded flag |
| [339906386 / S01](../../candidates/tic-339906386-s01/README.md) | 1.48428014 | 6183.5 | no recorded flag |
| [33999794 / S01](../../candidates/tic-33999794-s01/README.md) | 0.48331482 | 1462.8 | no recorded flag |
| [34064739 / S01](../../candidates/tic-34064739-s01/README.md) | 4.88277092 | 5664.3 | no recorded flag |
| [341916921 / S01](../../candidates/tic-341916921-s01/README.md) | 1.18960675 | 312.1 | no recorded flag |
| [35788575 / S01](../../candidates/tic-35788575-s01/README.md) | 9.64291030 | 4885.5 | no recorded flag |
| [360617400 / S01](../../candidates/tic-360617400-s01/README.md) | 0.60513406 | 1214.4 | no recorded flag |
| [362372394 / S01](../../candidates/tic-362372394-s01/README.md) | 1.99200824 | 10408.8 | no recorded flag |
| [364953731 / S01](../../candidates/tic-364953731-s01/README.md) | 13.33477372 | 12398.5 | no recorded flag |
| [365363321 / S01](../../candidates/tic-365363321-s01/README.md) | 5.83399104 | 4601.5 | no recorded flag |
| [365899880 / S01](../../candidates/tic-365899880-s01/README.md) | 14.37124388 | 23558.5 | no recorded flag |
| [380007573 / S01](../../candidates/tic-380007573-s01/README.md) | 1.74291143 | 5427.7 | no recorded flag |
| [384268936 / S01](../../candidates/tic-384268936-s01/README.md) | 2.41820268 | 6495.5 | no recorded flag |
| [387220183 / S01](../../candidates/tic-387220183-s01/README.md) | 13.11999977 | 301.1 | no recorded flag |
| [390325440 / S01](../../candidates/tic-390325440-s01/README.md) | 3.03277444 | 2033.0 | no recorded flag |
| [390438806 / S01](../../candidates/tic-390438806-s01/README.md) | 1.04604644 | 1964.8 | no recorded flag |
| [395511355 / S01](../../candidates/tic-395511355-s01/README.md) | 0.49073072 | 5210.4 | flagged |
| [402682058 / S01](../../candidates/tic-402682058-s01/README.md) | 1.71180008 | 1293.7 | no recorded flag |
| [403443129 / S01](../../candidates/tic-403443129-s01/README.md) | 2.81741862 | 22283.0 | flagged |
| [40588332 / S01](../../candidates/tic-40588332-s01/README.md) | 0.91485048 | 281.5 | no recorded flag |
| [406803545 / S01](../../candidates/tic-406803545-s01/README.md) | 0.84707432 | 1446.8 | no recorded flag |
| [409652504 / S01](../../candidates/tic-409652504-s01/README.md) | 2.00058851 | 3084.4 | no recorded flag |
| [410279702 / S01](../../candidates/tic-410279702-s01/README.md) | 14.93256844 | 237.7 | no recorded flag |
| [411812299 / S01](../../candidates/tic-411812299-s01/README.md) | 1.88814907 | 4387.6 | no recorded flag |
| [413415228 / S01](../../candidates/tic-413415228-s01/README.md) | 1.64314912 | 1548.0 | no recorded flag |
| [415107554 / S01](../../candidates/tic-415107554-s01/README.md) | 12.92950490 | 6398.9 | no recorded flag |
| [419165427 / S01](../../candidates/tic-419165427-s01/README.md) | 2.36751358 | 5904.1 | no recorded flag |
| [420357796 / S01](../../candidates/tic-420357796-s01/README.md) | 3.45098472 | 2137.6 | no recorded flag |
| [420631795 / S01](../../candidates/tic-420631795-s01/README.md) | 0.78091733 | 5470.9 | flagged |
| [423023660 / S01](../../candidates/tic-423023660-s01/README.md) | 1.37219086 | 14133.1 | flagged |
| [423516560 / S01](../../candidates/tic-423516560-s01/README.md) | 1.79830793 | 8675.1 | flagged |
| [424768689 / S01](../../candidates/tic-424768689-s01/README.md) | 1.74154579 | 3087.0 | no recorded flag |
| [426426820 / S01](../../candidates/tic-426426820-s01/README.md) | 0.87286225 | 823.7 | no recorded flag |
| [435985610 / S01](../../candidates/tic-435985610-s01/README.md) | 2.01267483 | 3464.1 | no recorded flag |
| [437928704 / S01](../../candidates/tic-437928704-s01/README.md) | 2.11850560 | 2623.3 | no recorded flag |
| [438599291 / S01](../../candidates/tic-438599291-s01/README.md) | 0.81636260 | 1158.4 | no recorded flag |
| [438641120 / S01](../../candidates/tic-438641120-s01/README.md) | 8.22935016 | 3795.8 | no recorded flag |
| [439164098 / S01](../../candidates/tic-439164098-s01/README.md) | 9.26720150 | 3236.4 | no recorded flag |
| [446959769 / S01](../../candidates/tic-446959769-s01/README.md) | 7.65988111 | 3437.4 | no recorded flag |
| [447012655 / S01](../../candidates/tic-447012655-s01/README.md) | 1.61260427 | 3130.9 | no recorded flag |
| [449695755 / S01](../../candidates/tic-449695755-s01/README.md) | 0.88457749 | 1272.1 | no recorded flag |
| [450380114 / S01](../../candidates/tic-450380114-s01/README.md) | 2.30094874 | 2613.7 | no recorded flag |
| [450587004 / S01](../../candidates/tic-450587004-s01/README.md) | 4.23944571 | 10772.4 | no recorded flag |
| [450790574 / S01](../../candidates/tic-450790574-s01/README.md) | 4.04797828 | 3699.8 | no recorded flag |
| [450867025 / S01](../../candidates/tic-450867025-s01/README.md) | 1.45508916 | 3442.4 | no recorded flag |
| [454377816 / S01](../../candidates/tic-454377816-s01/README.md) | 5.78977039 | 1307.2 | no recorded flag |
| [454591748 / S01](../../candidates/tic-454591748-s01/README.md) | 1.75134644 | 664.0 | flagged |
| [455311098 / S01](../../candidates/tic-455311098-s01/README.md) | 2.58490410 | 3212.7 | no recorded flag |
| [455325214 / S01](../../candidates/tic-455325214-s01/README.md) | 1.03693740 | 2362.8 | no recorded flag |
| [455978103 / S01](../../candidates/tic-455978103-s01/README.md) | 5.66426163 | 2407.5 | no recorded flag |
| [457537281 / S01](../../candidates/tic-457537281-s01/README.md) | 0.85189624 | 3378.2 | no recorded flag |
| [463538362 / S01](../../candidates/tic-463538362-s01/README.md) | 1.46719874 | 3080.8 | no recorded flag |
| [464857630 / S01](../../candidates/tic-464857630-s01/README.md) | 1.28712954 | 7174.8 | no recorded flag |
| [465040244 / S01](../../candidates/tic-465040244-s01/README.md) | 0.90662305 | 7454.3 | no recorded flag |
| [465932801 / S01](../../candidates/tic-465932801-s01/README.md) | 7.49820351 | 1389.8 | no recorded flag |
| [466146018 / S01](../../candidates/tic-466146018-s01/README.md) | 4.36261406 | 12774.2 | no recorded flag |
| [46693311 / S01](../../candidates/tic-46693311-s01/README.md) | 1.25744167 | 567.1 | no recorded flag |
| [467059462 / S01](../../candidates/tic-467059462-s01/README.md) | 1.13072694 | 18193.1 | no recorded flag |
| [467193799 / S01](../../candidates/tic-467193799-s01/README.md) | 5.92773724 | 1536.8 | no recorded flag |
| [46806792 / S01](../../candidates/tic-46806792-s01/README.md) | 1.96780698 | 938.1 | no recorded flag |
| [48061356 / S01](../../candidates/tic-48061356-s01/README.md) | 2.26204079 | 12550.1 | no recorded flag |
| [50020789 / S01](../../candidates/tic-50020789-s01/README.md) | 0.90145937 | 1813.3 | no recorded flag |
| [5508653 / S01](../../candidates/tic-5508653-s01/README.md) | 0.95356498 | 2164.1 | no recorded flag |
| [58146626 / S01](../../candidates/tic-58146626-s01/README.md) | 0.86754905 | 4032.8 | no recorded flag |
| [58634613 / S01](../../candidates/tic-58634613-s01/README.md) | 1.35952503 | 3399.5 | flagged |
| [59662756 / S01](../../candidates/tic-59662756-s01/README.md) | 5.27714949 | 9089.3 | no recorded flag |
| [68415069 / S01](../../candidates/tic-68415069-s01/README.md) | 0.76337248 | 1424.6 | no recorded flag |
| [71826274 / S01](../../candidates/tic-71826274-s01/README.md) | 3.71232229 | 744.9 | no recorded flag |
| [72632902 / S01](../../candidates/tic-72632902-s01/README.md) | 1.28984715 | 8182.7 | no recorded flag |
| [73254448 / S01](../../candidates/tic-73254448-s01/README.md) | 0.62307545 | 1549.3 | no recorded flag |
| [73597516 / S01](../../candidates/tic-73597516-s01/README.md) | 1.78896516 | 3087.0 | no recorded flag |
| [74743490 / S01](../../candidates/tic-74743490-s01/README.md) | 0.84730942 | 4217.0 | flagged |
| [7475565 / S01](../../candidates/tic-7475565-s01/README.md) | 0.87847921 | 2863.7 | no recorded flag |
| [82102762 / S01](../../candidates/tic-82102762-s01/README.md) | 10.03229598 | 17600.7 | flagged |
| [94012748 / S01](../../candidates/tic-94012748-s01/README.md) | 6.90745441 | 10878.1 | flagged |

The [immutable evidence release](https://github.com/brahle/exoplanet-candidates/releases/tag/run5-v0.1.0) was published on 2026-10-11 at 08:55:04 UTC. Locked dossiers are version 0.1.1; version 0.1.2 in the live catalogue records the release receipt without changing scientific evidence.

The [public evidence inspection certificate](public-evidence-certificate.json) verifies unauthenticated asset retrieval, all 171 manifest entries, 172 dossier validations and 17 tests in a fresh environment. It does not certify a numerical rerun.
