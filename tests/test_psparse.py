import unittest
import sys
from decimal import Decimal

from src.grammar_tester.psparse import strip_token, parse_tokens, parse_links, parse_postscript, get_link_set, \
    prepare_tokens, skip_command_response, skip_linkage_header, PS_TIMEOUT_EXPIRED, PS_PANIC_DETECTED, \
    get_sentence_text, split_ps_parses, trim_garbage, get_linkage_cost
from src.common.optconst import *
from src.grammar_tester.parsestat import parse_metrics


gutenberg_children_bug = \
"""
[(LEFT-WALL)(")(project.v)(gutenberg[?].n)('s.p)(alice[?].n)('s.p)(adventures.n)([in])(wonderland.n)
(,)(by)(lewis[!])(carroll[?].n)(")(()(edited.v-d)())]
[[0 2 1 (Wi)][0 1 0 (ZZZ)][2 9 2 (Os)][6 9 1 (Ds**x)][5 6 0 (YS)][4 5 0 (D*u)][3 4 0 (YS)]
[7 9 0 (AN)][9 11 1 (MXsx)][10 11 0 (Xd)][11 17 2 (Xc)][11 13 1 (Jp)][12 13 0 (AN)][13 16 1 (MXsp)]
[16 17 0 (Xca)][13 14 0 (ZZZ)][15 16 0 (Xd)]]
[0]
"""
gutenberg_children_bug2 = "[ebook # @number@ ][(LEFT-WALL)(release.n)(date.n)(:.j)(@date@[?].n)([)(ebook[?].a)([#])" \
                          "(@number@[?].n)(])][[0 3 2 (Xx)][0 2 1 (Wa)][1 2 0 (AN)][3 4 0 (Jp)][4 8 2 (MXs)]" \
                          "[5 8 1 (Xd)][6 8 0 (A)][8 9 0 (Xc)]][0]"


# cleaned_Gutenberg_Children bug list
cgch_bug_001 = \
"""
[ illustration : " i tell you what , you stay right here ! "[(LEFT-WALL)([[])(illustration.n-u)(:.v)(")([i])(tell.v)(you)(what)(,)(you)(stay.v)(right.a)(here)(!)(")][[0 14 4 (Xp)][0 9 3 (Xx)][0 6 2 (WV)][0 2 0 (Wd)][2 3 0 (Ss)][3 6 1 (I*v)][3 4 0 (ZZZ)][6 8 1 (QI)][6 7 0 (Ox)][9 11 1 (WV)][9 10 0 (Wd)][10 11 0 (Sp)][11 12 0 (Pa)][12 13 0 (MVp)][14 15 0 (ZZZ)]][0]
"""
# most people start at our web site which has the main pg search facility:
alice_bug_001 = \
"""
[(most)(people)(start)(at)([our])(web)(site)([which])([has])([the])
([main])([pg])([search])([facility:])]
[[0 1 0 (C26C33)][1 2 0 (C33C54)][2 3 0 (C54C22)][3 6 1 (C22C17)][5 6 0 (C23C17)]]
[0]
"""

# its business office is located at @number@ north @number@ west, salt lake city, ut @number@ , ( @number@ ) @number@ - @number@ , email business@pglaf.org.
alice_bug_002 = \
"""
[(LEFT-WALL)(its)(business.n-u)(office.n)(is.v)(located.v-d)(at)(@number@[?].n)(north.a)(@number@[?].a)
(west.a)(,)(salt.n-u)(lake.n)(city.n)(,)(ut[?].v)(@number@[?].a)(,)([(])
(@number@[?].a)())(@number@[?].a)(-.r)(@number@[?].a)(,)(email.s)(business@pglaf.org[?].n)(.)]
[[0 28 6 (Xp)][0 16 5 (WV)][0 11 4 (Xx)][0 5 3 (WV)][0 3 2 (Wd)][1 3 1 (Ds**x)][2 3 0 (AN)]
[3 4 0 (Ss*s)][4 5 0 (Pv)][5 9 1 (Pa)][5 6 0 (MVp)][6 7 0 (Jp)][7 8 0 (Mp)][9 10 0 (MVp)]
[11 15 3 (Xx)][15 16 0 (Wa)][11 14 2 (Wa)][12 14 1 (AN)][13 14 0 (AN)][16 27 5 (Os)][26 27 0 (AN)]
[17 26 4 (A)][17 18 0 (Xc)][20 26 3 (A)][20 21 0 (Xc)][22 26 2 (A)][22 23 0 (Xc)][24 26 1 (A)]
[24 25 0 (Xc)]]
[0]
"""

alice_bug_003 = \
"""
[(LEFT-WALL)([(])(alice[?].n)(had.v-d)(no.misc-d)(idea.n)(what)(latitude.n-u)(was.v-d)(,)
(or.ij)(longitude.n-u)(either.r)(,)([but])(thought.q-d)(they)(were.v-d)(nice.a)(grand.a)
(words.n)(to.r)(say.v)(.)([)])]
[[0 23 5 (Xp)][0 10 3 (Xx)][0 3 1 (WV)][0 2 0 (Wd)][2 3 0 (Ss)][3 5 1 (Os)][4 5 0 (Ds**x)]
[5 6 0 (MXs)][6 9 2 (Xca)][9 10 0 (Xd)][6 8 1 (Bsdt)][6 7 0 (Rn)][7 8 0 (Ss)][10 17 4 (WV)]
[10 11 0 (Wdc)][11 17 3 (Ss)][12 17 2 (E)][15 17 1 (Eq)][13 15 0 (Xd)][15 16 0 (SIpj)][17 20 2 (Opt)]
[18 20 1 (A)][19 20 0 (A)][20 22 1 (Bpw)][20 21 0 (R)][21 22 0 (I)]]
[0]
"""

alice_bug_004 = \
"""
[(LEFT-WALL)(posting.g)(date.n)(:.j)(@date@[?].a)([)(ebook[?].a)([#])(@number@[?].n)(])
(release.n)(date.n)(:.j)([@date@])(last.ord)(updated.v-d)(:.v)(@date@[?].n)]
[[0 3 2 (Xx)][0 2 1 (Wa)][1 2 0 (AN)][3 12 5 (Xx)][3 11 4 (Wa)][10 11 0 (AN)][4 10 3 (A)]
[4 8 2 (MX*ta)][5 8 1 (Xd)][6 8 0 (A)][8 9 0 (Xc)][12 16 2 (WV)][12 14 0 (Wd)][14 16 1 (Ss*o)]
[14 15 0 (Mv)][16 17 0 (Ost)]]
[0]
"""

gutenberg_children_bug_002 = \
"""
[(LEFT-WALL)([a])(millennium.n-u)(fulcrum.n)(edition.n)([(])([c])([)])(1991[!])([by])
(duncan[?].n)(research.n-u)]
[[0 11 5 (Wa)][2 11 4 (AN)][3 11 3 (AN)][4 11 2 (AN)][8 11 1 (AN)][10 11 0 (AN)]]
[0]
"""

gutenberg_children_bug_002t = "[(LEFT-WALL)([a])(millennium.n-u)(fulcrum.n)(edition.n)([(])([c])([)])(1991[!])([by])" \
                              "(duncan[?].n)(research.n-u)]"

gutenberg_children_bug_002tr = [r"###LEFT-WALL###", "[a]", "millennium", "fulcrum", "edition", "[(]", "[c]", "[)]",
                                "1991", "[by]", "duncan", "research"]

gutenberg_children_bug_002l = "[[0 11 5 (Wa)][2 11 4 (AN)][3 11 3 (AN)][4 11 2 (AN)][8 11 1 (AN)][10 11 0 (AN)]][0]"

gutenberg_children_bug_002lr = [(0, 11), (2, 11), (3, 11), (4, 11), (8, 11), (10, 11)]

explosion_bug = \
"""
conclusions : icp-sf-ms is a reliable method of blood analysis for cd , mn and pb even for the evaluation on an individual basis.
by comparing eyebrow shape and position in both young and mature women , this study provides objective data with which to plan forehead rejuvenating procedures.
the odds of being overweight in adulthood was @number@ times greater ( @percent@ ci : @date@ @number@ ) in overweight compared with healthy weight youth.
holocaust survivors did not differ in the level of resilience from comparisons ( mean : @number@ ± @number@ vs. @number@ ± @number@ respectively ) .
[(LEFT-WALL)(holocaust.n)(survivors.n)(did.v-d)(not.e)(differ.v)(in.r)(the)(level.n)(of)
(resilience.n-u)(from)(comparisons.n)(()(mean.a)([:])(@number@[?].n)(±[?].n)(@number@[?].n)(vs.)
(@number@[?].n)(±[?].n)(@number@[?].n)([respectively])())(.)]
[[0 25 4 (Xp)][0 5 2 (WV)][0 2 1 (Wd)][1 2 0 (AN)][2 3 0 (Sp)][3 5 1 (I*d)][3 4 0 (N)]
[4 5 0 (En)][5 11 2 (MVp)][5 6 0 (MVp)][6 8 1 (Js)][7 8 0 (Ds**c)][8 9 0 (Mf)][9 10 0 (Jp)]
[10 11 0 (Mp)][11 12 0 (Jp)][12 18 3 (MXp)][13 18 2 (Xd)][14 18 1 (A)][17 18 0 (AN)][16 17 0 (AN)]
[18 24 3 (Xc)][18 19 0 (Mp)][19 22 2 (Jp)][20 22 1 (AN)][21 22 0 (AN)]]
[0]
"""

timeout_linkage = \
"""
No complete linkages found.
Timer is expired!
Entering "panic" mode...
Found 576744359 linkages (100 of 100 random linkages had no P.P. violations) at null count 4
	Linkage 1, cost vector = (UNUSED=4 DIS= 0.00 LEN=19)
[(but)([I])(have)(passed)(my)(royal)(word)([,])(and)([I])
(cannot)(break)(it)([,])(so)(there)(is)(no)(help)(for)
(you)(..y)(')]
[[0 5 1 (FK)][0 2 0 (FF)][2 3 0 (FC)][3 4 0 (CJ)][5 10 1 (KG)][5 6 0 (KH)][8 10 0 (BG)]
[10 12 1 (GE)][11 12 0 (CE)][12 14 0 (EF)][14 20 2 (FF)][18 20 1 (CF)][17 18 0 (JC)][16 17 0 (LJ)]
[15 16 0 (EL)][18 19 0 (CB)][20 22 1 (FC)][21 22 0 (CC)]]
[0]
"""

sharp_sign_ps_tokens = \
"""
(LEFT-WALL)(but.ij)(there.#their)(still.n)(remained.v-d)(all.a)(the)(damage.n-u)(that.j-p)(had.v-d)
(been.v)([done])(that.j-r)(day.r)(,)(and.ij)(the)(king.n)(had.v-d)(nothing)
([with])([which])(to.r)(pay.v)(for.p)(this.p)(.)
"""

# [[0 26 6 (Xp)][0 23 5 (WV)][0 15 4 (Xx)][0 10 3 (WV)][0 1 0 (Wc)][1 4 2 (WV)][1 3 1 (Wdc)]
# [3 4 0 (Ss*s)][2 3 0 (Ds**c)][4 5 0 (O)][5 7 1 (Ju)][7 10 1 (Bs*t)][5 6 0 (ALx)][6 7 0 (Dmu)]
# [7 8 0 (Rn)][8 9 0 (Ss*b)][9 10 0 (PPf)][10 13 1 (MVpn)][12 13 0 (DTn)][14 15 0 (Xd)][15 18 2 (WV)]
# [15 17 1 (Wdc)][17 18 0 (Ss*s)][16 17 0 (Ds**c)][18 22 1 (MVi)][22 23 0 (I)][18 19 0 (Os)][23 24 0 (MVp)]
# [24 25 0 (Js)]]
# [0]
# """

sharp_sign_tokens = \
["###LEFT-WALL###", "but", "there", "still", "remained", "all", "the", "damage", "that", "had",
"been", "[done]", "that", "day", ",", "and", "the", "king", "had", "nothing", "[with]", "[which]",
 "to", "pay", "for", "this", "."]

sharp_sign_ps_linkages = \
"""
[(LEFT-WALL)(but.ij)(there.#their)(still.n)(remained.v-d)(all.a)(the)(damage.n-u)(that.j-p)(had.v-d)
(been.v)([done])(that.j-r)(day.r)(,)(and.ij)(the)(king.n)(had.v-d)(nothing)
([with])([which])(to.r)(pay.v)(for.p)(this.p)(.)]
[[0 26 6 (Xp)][0 23 5 (WV)][0 15 4 (Xx)][0 10 3 (WV)][0 1 0 (Wc)][1 4 2 (WV)][1 3 1 (Wdc)]
[3 4 0 (Ss*s)][2 3 0 (Ds**c)][4 5 0 (O)][5 7 1 (Ju)][7 10 1 (Bs*t)][5 6 0 (ALx)][6 7 0 (Dmu)]
[7 8 0 (Rn)][8 9 0 (Ss*b)][9 10 0 (PPf)][10 13 1 (MVpn)][12 13 0 (DTn)][14 15 0 (Xd)][15 18 2 (WV)]
[15 17 1 (Wdc)][17 18 0 (Ss*s)][16 17 0 (Ds**c)][18 22 1 (MVi)][22 23 0 (I)][18 19 0 (Os)][23 24 0 (MVp)]
[24 25 0 (Js)]]
[0]
"""

sharp_sign_links = {
    (0, 26), (0, 23), (0, 15), (0, 10), (0, 1), (1, 4), (1, 3), (3, 4), (2, 3), (4, 5), (5, 7), (7, 10), (5, 6), (6, 7),
    (7, 8), (8, 9), (9, 10), (10, 13), (12, 13), (14, 15), (15, 18), (15, 17), (17, 18), (16, 17), (18, 22), (22, 23),
    (18, 19), (23, 24), (24, 25)
}

# panic_linkage_01 = \
# """
# ' No , ' said Gerda , and she told all that had happened to her , and how dearly she loved little Kay.
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 11038 linkages (16 of 100 random linkages had no P.P. violations) at null count 7
#         Linkage 1, cost vector = (UNUSED=7 DIS=12.10 LEN=25)
# [(LEFT-WALL)(['])([No])(,)(['])(said.q-d)(Gerda.f)(,)(and.ij)(she)
# (told.v-d)(all.a)(that.j-r)(had.v-d)(happened.v-d)(to.r)(her)([,])([and])(how)
# (dearly)(she)(loved.v-d)(little.i)(Kay.f)([.])(RIGHT-WALL)]
# [[0 8 2 (Wc)][7 8 0 (Xd)][5 7 1 (Xc)][3 5 0 (Xd)][5 6 0 (SIsj)][8 10 1 (WV)][8 9 0 (Wdc)]
# [9 10 0 (Ss)][10 19 3 (QI*d)][10 15 2 (MVp)][10 11 0 (O)][11 13 1 (B)][11 12 0 (R)][12 13 0 (RS)]
# [13 14 0 (PPf)][15 16 0 (J)][19 20 0 (EEh)][20 22 1 (CV)][20 21 0 (Ca)][21 22 0 (Ss)][22 24 1 (Osne)]
# [22 23 0 (MVa)]]
# [0]
# """
#
# panic_linkage_02 = \
# """
# He was getting on well with his learning , but another hundred dollars were needed , as they must have more books.
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 27 linkages (27 had no P.P. violations) at null count 3
#         Linkage 1, cost vector = (UNUSED=3 DIS=14.72 LEN=41)
# [(LEFT-WALL)(he)(was.v-d)(getting.v)(on)(well.n-u)(with)(his)(learning.q)(,)
# (but.ij)(another)([hundred])([dollars])(were.v-d)(needed.v-d)([,])(as.#while)(they)(must.v)
# (have.v)(more)(books.n)(.)]
# [[0 2 1 (WV)][0 1 0 (Wd)][1 2 0 (Ss)][2 3 0 (Pg*b)][3 15 4 (MVg)][3 6 2 (MVp)][3 5 1 (Oun)]
# [3 4 0 (K)][6 8 1 (Pg)][8 15 3 (Xd)][6 7 0 (J)][8 14 2 (WV)][8 10 1 (Wc)][8 9 0 (Xca)]
# [9 10 0 (Xd)][10 11 0 (Wdc)][11 14 0 (Ss*s)][15 23 2 (Xc)][15 17 0 (MVs)][17 20 1 (CV)][17 18 0 (Cs)]
# [18 19 0 (Sp)][19 20 0 (If)][20 22 1 (Op)][21 22 0 (Dmcm)]]
# [0]
# """
#
# panic_linkage_03 = \
# """
# But there still remained all the damage that had been done that day , and the king had nothing with which to pay for this.
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 27061933 linkages (0 of 100 random linkages had no P.P. violations) at null count 5
# There was nothing else to be done than to try to answer the troll's riddles.
# Found 9901 linkages (226 of 1000 random linkages had no P.P. violations)
#         Linkage 1, cost vector = (UNUSED=0 DIS= 4.80 LEN=39)
# [(LEFT-WALL)(there.r)(was.v-d)(nothing)(else)(to.r)(be.v)(done.a)(than.#then-r)(to.r)
# (try.v)(to.r)(answer.v)(the)(troll.n)('s.v)(riddles.n)(.)]
# [[0 17 4 (Xp)][0 8 2 (Xs)][0 2 1 (WV)][0 1 0 (Wd)][1 2 0 (SFst)][2 5 1 (MVi)][2 3 0 (Ost)]
# [3 4 0 (EL)][5 6 0 (Ix)][6 7 0 (Pa)][7 8 0 (MVs)][8 15 3 (CV)][8 9 0 (Cs)][9 15 2 (SFsx)]
# [9 10 0 (I)][10 12 1 (IV)][10 11 0 (TO)][11 12 0 (I*t)][12 14 1 (Os)][13 14 0 (Ds**c)][15 16 0 (Opt)]]
# [0]
# """
#
# panic_linkage_04 = \
# """
# She remembered Aveline's warning , and tried to turn her horse , but it stood as still as if it had been marble.
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 4056 linkages (38 of 100 random linkages had no P.P. violations) at null count 2
#         Linkage 1, cost vector = (UNUSED=2 DIS=10.46 LEN=42)
# [(LEFT-WALL)(she)(remembered.v-d)(Aveline[!])('s.p)(warning.g)(,)(and.j-v)(tried.v-d)(to.r)
# (turn.v)(her)(horse.n-m)(,)(but.misc-ex)(it)(stood.v-d)(as.e)(still.n)([as])
# ([if])(it)(had.v-d)(been.v)(marble.v)(.)]
# [[0 7 4 (WV)][0 1 0 (Wd)][1 7 3 (Ss)][2 7 2 (VJlsi)][2 5 1 (Os)][4 5 0 (Dmu)][3 4 0 (YS)]
# [6 7 0 (Xd)][7 8 0 (VJrsi)][8 10 1 (IV)][8 9 0 (TO)][9 10 0 (I*t)][10 14 2 (MVx)][10 12 1 (Os)]
# [11 12 0 (Ds**c)][13 14 0 (Xd)][14 25 2 (Xc)][14 18 1 (Jk)][17 18 0 (Js)][16 17 0 (MVp)][15 16 0 (Ss)]
# [18 24 1 (Bsd)][18 21 0 (Rn)][21 22 0 (Ss)][22 23 0 (PPf)][23 24 0 (I*v)]]
# [0]
# """
#
# panic_linkage_05 = \
# """
# ' Do you think so ? ' said the carpenter ; ' I can well believe it , for I am indeed very poorly. '
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 100 linkages (15 had no P.P. violations) at null count 5
#         Linkage 1, cost vector = (UNUSED=5 DIS= 9.73 LEN=50)
# [(LEFT-WALL)(['])(Do[!])(you)(think.v)(so.e)(?)(['])(said.q-d)(the)
# (carpenter.n)(;)(['])(I.p)(can.v)(well.e)(believe.q)([it])(,)(for.r)
# (I.p)(am.v)(indeed)(very.e)(poorly.e)(.)(['])]
# [[0 11 4 (Xx)][0 8 3 (CPx)][8 11 2 (Xca)][0 4 2 (WV)][0 3 1 (Wd)][3 4 0 (Sp)][2 3 0 (COa)]
# [4 5 0 (O)][6 8 0 (Xq)][8 10 1 (SIsj)][9 10 0 (Ds**c)][11 16 2 (WV)][11 13 0 (Wd)][13 14 0 (Sp*i)]
# [14 16 1 (I)][15 16 0 (E)][16 25 3 (Xp)][16 21 2 (WV)][16 19 1 (Wc)][16 18 0 (Xc)][19 20 0 (Wd)]
# [20 21 0 (SX)][21 24 1 (MVa)][21 22 0 (MVa)][23 24 0 (EE)]]
# [0]
# """
#
# panic_linkage_06 = \
# """
# ' You must have a bath set in your room , O queen , ' said she , ' and filled with running water.
# No complete linkages found.
# Timer is expired!
# Entering "panic" mode...
# Found 19931 linkages (78 of 100 random linkages had no P.P. violations) at null count 5
# <------>Linkage 1, cost vector = (UNUSED=5 DIS= 8.66 LEN=34)
# [(LEFT-WALL)(['])(You[!])(must.v)(have.v)(a)(bath.n)(set.v-d)(in.r)(your)
# (room.s)([,])(O.id)(queen.n)(,)(['])(said.q-d)(she)(,)(['])
# ([and])(filled.v-d)(with)(running.v)(water.n-u)(.)]
# [[0 7 3 (WV)][0 2 0 (Wd)][2 3 0 (Ss*s)][3 4 0 (If)][4 7 2 (Pv)][4 6 1 (Os)][5 6 0 (Ds**c)]
# [7 8 0 (MVp)][8 13 3 (Js)][9 13 2 (Ds**x)][10 13 1 (AN)][10 12 0 (NMa)][13 21 2 (MXsp)][18 21 0 (Xd)]
# [16 18 1 (Xc)][14 16 0 (Xd)][16 17 0 (SIsj)][21 25 1 (Xc)][21 22 0 (MVp)][22 23 0 (Mgp)][23 24 0 (Ou)]]
# [0]
# """


merged_ps_parses = \
"""
here the train was coming mother was holding Jem's hand Dog Monday was licking it everybody was saying good-bye the train was in !
No complete linkages found.
Found 38230999 linkages (0 of 1000 random linkages had no P.P. violations) at null count 2
They had gone.
Found 2 linkages (2 had no P.P. violations)
        Linkage 1, cost vector = (UNUSED=0 DIS= 0.00 LEN=5)
[(LEFT-WALL)(they)(had.v-d)(gone.v)(.)]
[[0 4 2 (Xp)][0 3 1 (WV)][0 1 0 (Wd)][1 2 0 (Sp)][2 3 0 (PP)]]
[0]
"""

merged_ps_parses2 = \
"""
There the train was coming mother was holding Jem's hand Dog Monday was licking it everybody was saying good-bye the train was in !
No complete linkages found.
Found 38230999 linkages (0 of 1000 random linkages had no P.P. violations) at null count 2
Here comes the sun, here comes the sun, it's alright !
No complete linkages found.
Found 38230999 linkages (0 of 1000 random linkages had no P.P. violations) at null count 2
They had gone.
Found 2 linkages (2 had no P.P. violations)
        Linkage 1, cost vector = (UNUSED=0 DIS= 0.00 LEN=5)
[(LEFT-WALL)(they)(had.v-d)(gone.v)(.)]
[[0 4 2 (Xp)][0 3 1 (WV)][0 1 0 (Wd)][1 2 0 (Sp)][2 3 0 (PP)]]
[0]
"""

merged_ps_parses3 = \
"""
They had gone.
Found 2 linkages (2 had no P.P. violations)
        Linkage 1, cost vector = (UNUSED=0 DIS= 0.00 LEN=5)
[(LEFT-WALL)(they)(had.v-d)(gone.v)(.)]
[[0 4 2 (Xp)][0 3 1 (WV)][0 1 0 (Wd)][1 2 0 (Sp)][2 3 0 (PP)]]
[0]
"""

two_linkages_ps = \
"""
the old beast was whinnying on his shoulder .
No complete linkages found.
Found 3 linkages (3 had no P.P. violations) at null count 2
        Linkage 1, cost vector = (UNUSED=2 DIS= 0.00 LEN=6)
[(the)([old])(beast)(was)([whinnying])(on)(his)(shoulder)(.)]
[[0 2 0 (SYER)][2 7 1 (EREF)][6 7 0 (ODEF)][5 6 0 (LLOD)][3 5 0 (LXLL)][7 8 0 (EFAT)]]
[0]

        Linkage 2, cost vector = (UNUSED=2 DIS= 0.00 LEN=6)
[(the)([old])(beast)(was)([whinnying])(on)(his)(shoulder)(..y)]
[[0 2 0 (SYER)][2 7 1 (EREF)][6 7 0 (ODEF)][5 6 0 (LLOD)][3 5 0 (LXLL)][7 8 0 (EFAT)]]
[0]
"""


# two_linkages_ps = \
# """
# the old beast was whinnying on his shoulder .
# No complete linkages found.
# Found 3 linkages (3 had no P.P. violations) at null count 2
#         Linkage 1, cost vector = (UNUSED=2 DIS= 0.00 LEN=6)
# [(the)([old])(beast)(was)([whinnying])(on)(his)(shoulder)(.)]
# [[0 2 0 (SYER)][2 7 1 (EREF)][6 7 0 (ODEF)][5 6 0 (LLOD)][3 5 0 (LXLL)][7 8 0 (EFAT)]]
# [0]
#
#         Linkage 2, cost vector = (UNUSED=2 DIS= 0.00 LEN=6)
# [(the)([old])(beast)(was)([whinnying])(on)(his)(shoulder)(..y)]
# [[0 2 0 (SYER)][2 7 1 (EREF)][6 7 0 (ODEF)][5 6 0 (LLOD)][3 5 0 (LXLL)][7 8 0 (EFAT)]]
# [0]
#
# Jims lifted his miserable eyes .
# Found 2 linkages (2 had no P.P. violations)
#         Linkage 1, cost vector = (UNUSED=0 DIS= 0.00 LEN=5)
# [(jims)(lifted)(his)(miserable)(eyes)(.)]
# [[0 1 0 (BFAS)][1 5 2 (ASAT)][1 4 1 (ASOR)][1 2 0 (ASOD)][3 4 0 (CCOR)]]
# [0]
#
#         Linkage 2, cost vector = (UNUSED=0 DIS= 0.00 LEN=5)
# [(jims)(lifted)(his)(miserable)(eyes)(..y)]
# [[0 1 0 (BFAS)][1 5 2 (ASAT)][1 4 1 (ASOR)][1 2 0 (ASOD)][3 4 0 (CCOR)]]
# [0]
# """



# """
# postscript set to 1
# graphics set to 0
# echo set to 1
# verbosity set to 1
# link-grammar: Info: Dictionary found at /home/aglushchenko/anaconda3/envs/ull-lg551/share/link-grammar/en/4.0.dict
# link-grammar: Info: Dictionary version 5.5.1, locale en_US.UTF-8
# link-grammar: Info: Library version link-grammar-5.5.1. Enter "!help" for help.
# But there still remained all the damage that had been done that day , and the king had nothing with which to pay for this.
# No complete linkages found.
# Found 8706604 linkages (4 of 1000 random linkages had no P.P. violations) at null count 3
# 	Linkage 1, cost vector = (UNUSED=3 DIS= 7.85 LEN=84)
# [(LEFT-WALL)(but.ij)(there.#their)(still.n)(remained.v-d)(all.a)(the)(damage.n-u)(that.j-p)(had.v-d)
# (been.v)([done])(that.j-r)(day.r)(,)(and.ij)(the)(king.n)(had.v-d)(nothing)
# ([with])([which])(to.r)(pay.v)(for.p)(this.p)(.)]
# [[0 26 6 (Xp)][0 23 5 (WV)][0 15 4 (Xx)][0 10 3 (WV)][0 1 0 (Wc)][1 4 2 (WV)][1 3 1 (Wdc)]
# [3 4 0 (Ss*s)][2 3 0 (Ds**c)][4 5 0 (O)][5 7 1 (Ju)][7 10 1 (Bs*t)][5 6 0 (ALx)][6 7 0 (Dmu)]
# [7 8 0 (Rn)][8 9 0 (Ss*b)][9 10 0 (PPf)][10 13 1 (MVpn)][12 13 0 (DTn)][14 15 0 (Xd)][15 18 2 (WV)]
# [15 17 1 (Wdc)][17 18 0 (Ss*s)][16 17 0 (Ds**c)][18 22 1 (MVi)][22 23 0 (I)][18 19 0 (Os)][23 24 0 (MVp)]
# [24 25 0 (Js)]]
# [0]
# """

explosion_no_linkages = \
"""
But there still remained all the damage that had been done that day , and the king had nothing with which to pay for this.
No complete linkages found.
Timer is expired!
Entering "panic" mode...
link-grammar: Warning: Combinatorial explosion! nulls=5 cnt=27061933
Consider retrying the parse with the max allowed disjunct cost set lower.
At the command line, use !cost-max
Found 27061933 linkages (0 of 100 random linkages had no P.P. violations) at null count 5
"""

tuna_isa_fish_ps = \
"""
tuna isa fish.
Found 1 linkage (1 had no P.P. violations)
	Unique linkage, cost vector = (UNUSED=0 DIS= 0.00 LEN=4)
[(LEFT-WALL)(tuna.sff)(isa)(fish.of)(.)]
[[0 4 2 (Xp)][0 2 1 (WV)][0 1 0 (Wa)][1 2 0 (Sff)][2 3 0 (Of)]]
[0]
"""


lg_post_output = """
echo set to 1
postscript set to 1
graphics set to 0
verbosity set to 0
tuna has fin .
[(LEFT-WALL)(tuna)(has)(fin)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

eagle isa bird .
[(LEFT-WALL)(eagle)(isa)(bird)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

fin isa extremity .
[(LEFT-WALL)(fin)(isa)(extremity)(.)]
[[0 1 0 (C05C04)][1 2 0 (C04C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

tuna isa fish .
[(LEFT-WALL)(tuna)(isa)(fish)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

fin has scale .
[(LEFT-WALL)(fin)([has])(scale)(.)]
[[0 1 0 (C05C04)][1 3 0 (C04C04)][3 4 0 (C04C03)]]
[0]

eagle has wing .
[(LEFT-WALL)(eagle)(has)(wing)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

wing has feather .
[(LEFT-WALL)(wing)([has])(feather)(.)]
[[0 1 0 (C05C04)][1 3 0 (C04C04)][3 4 0 (C04C03)]]
[0]

wing isa extremity .
[(LEFT-WALL)(wing)(isa)(extremity)(.)]
[[0 1 0 (C05C04)][1 2 0 (C04C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

herring isa fish .
[(LEFT-WALL)(herring)(isa)(fish)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

herring has fin .
[(LEFT-WALL)(herring)(has)(fin)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

parrot isa bird .
[(LEFT-WALL)(parrot)(isa)(bird)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C06)][3 4 0 (C06C03)]]
[0]

parrot has wing .
[(LEFT-WALL)(parrot)(has)(wing)(.)]
[[0 1 0 (C05C02)][1 2 0 (C02C01)][2 3 0 (C01C04)][3 4 0 (C04C03)]]
[0]

Bye.
"""

sticky_parses_01 = \
"""
but if Kilmeny says she will not marry you I am afraid she 'll stick to it . "
No complete linkages found.
Timer is expired!
Entering "panic" mode...
Panic timer is expired!
" no , Master , it wouldn't be any use .
No complete linkages found.
Found 125746 linkages (100 of 100 random linkages had no P.P. violations) at null count 1
	Linkage 1, cost vector = (UNUSED=1 DIS= 0.00 LEN=8)
[(")(no)(,)([Master])(,)(it)(wouldn't)(be)(any)(use)
(.)]
[[0 6 1 (LG)][0 1 0 (LK)][1 2 0 (KN)][5 6 0 (DG)][4 5 0 (ND)][6 9 2 (GE)][6 8 1 (GK)]
[8 9 0 (KE)][7 8 0 (DK)][9 10 0 (EE)]]
[0]
"""


sticky_parses_02 = \
"""
but if Mahbub Ali did not know this , it would be very unsafe to tell him so .
No complete linkages found.
Timer is expired!
Entering "panic" mode...
Panic timer is expired!
Mahbub Ali was hard upon boys who knew , or thought they knew , too much .
No complete linkages found.
Timer is expired!
Found 13780061 linkages (15 of 16 random linkages had no P.P. violations) at null count 1
	Linkage 1, cost vector = (UNUSED=1 DIS= 0.00 LEN=26)
[(mahbub)([Ali])(was)(hard)(upon)(boys)(who)(knew)(,)(or)
(thought)(they)(knew)(,)(too)(much)(..y)]
[[0 15 3 (HL)][0 6 2 (HD)][4 6 1 (LD)][3 4 0 (EL)][2 3 0 (SE)][4 5 0 (LP)][6 11 2 (DD)]
[9 11 1 (DD)][8 9 0 (ND)][7 8 0 (GN)][9 10 0 (DG)][13 15 1 (NL)][12 13 0 (GN)][13 14 0 (NG)]
[15 16 0 (LF)]]
[0]
"""

sticky_parses_03 = \
"""
when the horse saw this it changed itself to a dove , and flew up into the air .
No complete linkages found.
Timer is expired!
Entering "panic" mode...
Panic timer is expired!
Found 2147483647 linkages (15 of 16 random linkages had no P.P. violations) at null count 1
        Linkage 1, cost vector = (UNUSED=1 DIS= 0.00 LEN=20)
[(when)(the)(horse)(saw)(this)(it)(changed)([itself])(to)(a)
(dove)(,)(and)(flew)(up.'and)(into)(the)(air)(.)]
[[0 6 2 (DE)][0 4 1 (DK)][3 4 0 (GK)][2 3 0 (PG)][1 2 0 (TP)][5 6 0 (DE)][6 11 2 (EN)]
[6 8 0 (EQ)][8 10 1 (QH)][9 10 0 (VH)][11 14 1 (NU)][13 14 0 (EU)][12 13 0 (RE)][14 18 2 (UE)]
[17 18 0 (PE)][15 17 1 (MP)][16 17 0 (TP)]]
[0]
"""

explosion_no_linkages_full = \
"""
echo set to 1
postscript set to 1
graphics set to 0
verbosity set to 1
timeout set to 1
limit set to 100
But there still remained all the damage that had been done that day , and the king had nothing with which to pay for this.
No complete linkages found.
Timer is expired!
Entering "panic" mode...
link-grammar: Warning: Combinatorial explosion! nulls=5 cnt=27061933
Consider retrying the parse with the max allowed disjunct cost set lower.
At the command line, use !cost-max
Found 27061933 linkages (0 of 100 random linkages had no P.P. violations) at null count 5
Bye.
"""


class TestPSParse(unittest.TestCase):

    post_all_walls = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)]" \
                     "[[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)]" \
                     "[4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
    post_no_walls = "[(eagle)(has)(wing)(.)][[0 2 1 (C04C01)][1 2 0 (C01C01)][2 3 0 (C01C05)]][0]"
    post_no_links = "[([herring])([isa])([fish])([.])][][0]"

    link_str = "[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]"

    tokens_all_walls = "(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)"
    tokens_no_walls = "(eagle)(has)(wing)(.)"
    tokens_no_walls_no_period = "(eagle)(has)(wing)"

    def test_trim_garbage(self):
        self.assertTrue(0 < trim_garbage(lg_post_output))
        self.assertTrue(0 < trim_garbage(explosion_no_linkages_full))
        self.assertTrue(0 < trim_garbage(explosion_no_linkages))
        self.assertTrue(0 < trim_garbage(sticky_parses_01))
        self.assertTrue(0 < trim_garbage(sticky_parses_02))

    def test_split_ps_parses(self):
        parses = split_ps_parses(merged_ps_parses)
        self.assertEqual(2, len(parses))

        parses = split_ps_parses(merged_ps_parses2)
        self.assertEqual(3, len(parses))

        parses = split_ps_parses(merged_ps_parses3)
        self.assertEqual(1, len(parses))

        parses = split_ps_parses(sticky_parses_01)
        self.assertEqual(2, len(parses))

        parses = split_ps_parses(sticky_parses_02)
        self.assertEqual(2, len(parses))

        parses = split_ps_parses(sticky_parses_03)
        self.assertEqual(1, len(parses))

    def test_get_sentence_text(self):
        parses = split_ps_parses(merged_ps_parses2)
        self.assertEqual(3, len(parses))

        self.assertEqual("There the train was coming mother was holding Jem's hand Dog Monday was licking it everybody "
                         "was saying good-bye the train was in !", get_sentence_text(parses[0]))

        self.assertEqual("Here comes the sun, here comes the sun, it's alright !", get_sentence_text(parses[1]))

        self.assertEqual("They had gone.", get_sentence_text(parses[2]))

        self.assertEqual("tuna isa fish.", get_sentence_text(tuna_isa_fish_ps))

        parses = split_ps_parses(sticky_parses_01)
        self.assertEqual(2, len(parses))

        self.assertEqual('but if Kilmeny says she will not marry you I am afraid she \'ll stick to it . "',
                         get_sentence_text(parses[0]))

        self.assertEqual('" no , Master , it wouldn\'t be any use .', get_sentence_text(parses[1]))

        parses = split_ps_parses(sticky_parses_02)
        self.assertEqual(2, len(parses))

        self.assertEqual('but if Mahbub Ali did not know this , it would be very unsafe to tell him so .',
                         get_sentence_text(parses[0]))

        self.assertEqual('Mahbub Ali was hard upon boys who knew , or thought they knew , too much .',
                         get_sentence_text(parses[1]))

        parses = split_ps_parses(two_linkages_ps)
        self.assertEqual(1, len(parses))

        self.assertEqual('the old beast was whinnying on his shoulder .',
                         get_sentence_text(parses[0]))
        #
        # self.assertEqual('Jims lifted his miserable eyes .',
        #                  get_sentence_text(parses[1]))



    @staticmethod
    def cmp_lists(list1: [], list2: []) -> bool:
        if list1 is None or list2 is None or len(list1) != len(list2):
            return False

        for i in range(0, len(list1)):
            if list1[i] != list2[i]:
                return False

        return True

    def test_strip_token(self):
        """ Test for stripping Link Grammar suffixes off tokens """
        self.assertEqual(strip_token("strange[!]"), "strange")
        self.assertEqual(strip_token("strange.a"), "strange")
        self.assertEqual(strip_token("[strange]"), "[strange]")
        self.assertEqual(strip_token("..y"), ".")
        self.assertEqual(strip_token("Lewis.b"), "Lewis")

    # @unittest.skip
    def test_parse_tokens_alice_003(self):
        """ Test for proper parsing of '[(]' revealed by Alice in Wonderland corpus """
        options = BIT_STRIP | BIT_NO_LWALL | BIT_NO_PERIOD

        # sent = "(alice had no idea what latitude was, or longitude either, but thought they were nice grand words to say.)"
        post = "(LEFT-WALL)([(])(alice[?].n)(had.v-d)(no.misc-d)(idea.n)(what)(latitude.n-u)(was.v-d)(,)(or.ij)" \
               "(longitude.n-u)(either.r)(,)([but])(thought.q-d)(they)(were.v-d)(nice.a)(grand.a)(words.n)(to.r)(say.v)" \
               "(.)([)])"
        ref = \
        ["###LEFT-WALL###", "[(]", "alice", "had", "no", "idea", "what", "latitude", "was", ",", "or", "longitude",
        "either", ",", "[but]", "thought", "they", "were", "nice", "grand", "words", "to", "say", ".", "[)]"]

        tokens = parse_tokens(post, options)[0]
        self.assertEqual(ref, tokens)

    # @unittest.skip
    def test_parse_tokens_alice_004(self):
        """ Test for proper parsing of square brackets revealed by Alice in Wonderland corpus """
        options = BIT_STRIP | BIT_NO_LWALL | BIT_NO_PERIOD

        post = "(LEFT-WALL)(posting.g)(date.n)(:.j)(@date@[?].a)([)(ebook[?].a)([#])(@number@[?].n)(])(release.n)" \
               "(date.n)(:.j)([@date@])(last.ord)(updated.v-d)(:.v)(@date@[?].n)"

        ref = ["###LEFT-WALL###", "posting", "date", ":", "@date@", "[", "ebook", "[#]", "@number@", "]", "release",
               "date", ":", "[@date@]", "last", "updated", ":", "@date@"]

        tokens = parse_tokens(post, options)[0]
        self.assertEqual(ref, tokens)

    # @unittest.skip
    def test_parse_tokens_sharp(self):
        """ Test for proper parsing of sharp sign prefixes """
        options = BIT_STRIP  # | BIT_NO_LWALL | BIT_NO_PERIOD

        # tokens = parse_tokens(sharp_sign_ps_tokens.replace("\n", ""), options)[0]

        tokens, links = parse_postscript(sharp_sign_ps_linkages, options)

        self.assertEqual(len(sharp_sign_tokens), len(tokens))
        self.assertEqual(sharp_sign_tokens, tokens)
        self.assertEqual(sharp_sign_links, set(links))

    # @unittest.skip
    def test_parse_tokens(self):
        """ test_parse_tokens """

        options = 0

        # No RIGHT-WALL, no CAPS
        options |= BIT_STRIP
        # tokens = parse_tokens(self.tokens_all_walls, options)
        # self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a',
        #                                         'parent', 'before', '.']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)[0]
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

        # RIGHT-WALL and CAPS, no STRIP
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens = parse_tokens(self.tokens_all_walls, options)[0]
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'Dad[!]', 'was.v-d', 'not.e', 'a',
                                                'parent.n', 'before', '.', '###RIGHT-WALL###']))

        # Tokens without walls
        tokens = parse_tokens(self.tokens_no_walls, options)[0]
        # print(tokens, file=sys.stdout)
        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing', '.']))

    @unittest.skip
    def test_parse_tokens_no_left_wall(self):
        # NO_LWALL and CAPS, no STRIP
        options = 0
        options |= BIT_CAPS | BIT_NO_LWALL
        # options |= (BIT_NO_LWALL | BIT_CAPS)
        # options &= (~(BIT_STRIP | BIT_RWALL))
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['Dad[!]', 'was.v-d', 'not.e', 'a',
                                                'parent.n', 'before', '.']))

    @unittest.skip
    def test_parse_tokens_no_walls_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_NO_LWALL
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['dad', 'was', 'not', 'a', 'parent', 'before']))

    @unittest.skip
    def test_parse_tokens_rwall_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_all_walls, options)[0]

        # print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before',
                                                '###RIGHT-WALL###']))

    @unittest.skip
    def test_parse_tokens_no_period(self):
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_no_walls, options)[0]

        print(tokens)

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing']))

    # @unittest.skip
    def test_parse_no_period_if_no_period(self):
        """ Test for parsing sentence with no walls and period """
        options = 0
        options |= BIT_STRIP | BIT_NO_PERIOD | BIT_RWALL
        tokens = parse_tokens(self.tokens_no_walls_no_period, options)[0]

        self.assertTrue(self.cmp_lists(tokens, ['###LEFT-WALL###', 'eagle', 'has', 'wing']))

    # @unittest.skip
    def test_parse_links(self):
        """ Test for parsing links out when LW and period are presented """
        links = parse_links(self.link_str, ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.'], 0)

        # [0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)][4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]
        self.assertTrue(self.cmp_lists(links, [  (0, 7),
                                                 (0, 1),
                                                 (1, 2),
                                                 (2, 5),
                                                 (2, 3),
                                                 (4, 5),
                                                 (5, 6) ]))

    # @unittest.skip
    def test_parse_postscript_all_walls(self):
        """ Test for parsing postscript with both walls in """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP
        tokens, links = parse_postscript(self.post_all_walls, options)
        pm = parse_metrics(tokens)
        self.assertEqual(1.0, pm.completely_parsed_ratio)
        self.assertEqual(0.0, pm.completely_unparsed_ratio)
        self.assertEqual(1.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_no_walls(self):
        """ Test for parsing_postscript with no walls in """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(self.post_no_walls, options)
        pm = parse_metrics(tokens)
        self.assertEqual(1.0, pm.completely_parsed_ratio)
        self.assertEqual(0.0, pm.completely_unparsed_ratio)
        self.assertEqual(1.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_no_links(self):
        """ Test for parsing postscript with no links """
        options = 0
        options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(self.post_no_links, options)
        self.assertEqual(0, len(links))

    @unittest.skip
    def test_parse_postscript_gutenchildren_bug(self):
        """ Test for number of tokens (bug from Gutenberg Children corpus) """
        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        # options &= ~BIT_STRIP

        tokens, links = parse_postscript(gutenberg_children_bug, options)

        self.assertEqual(18, len(tokens))

    @unittest.skip
    def test_parse_gutenchildren_bug_002(self):
        """ Test for number of tokens (bug from Gutenberg Children corpus) """
        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        tokens = parse_tokens(gutenberg_children_bug_002t, options)[0]

        self.assertEqual(tokens, gutenberg_children_bug_002tr)

    # @unittest.skip
    def test_parse_postscript_gutenchildren_bug_002(self):

        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        tokens, links = parse_postscript(gutenberg_children_bug_002, options)

        print(tokens)

        self.assertEqual(12, len(tokens))
        self.assertEqual(6, len(links))

        # pm = parse_metrics(tokens)
        #
        # self.assertEqual(0.0, pm.completely_parsed_ratio)
        # self.assertEqual(0.0, pm.completely_unparsed_ratio)
        # self.assertEqual(0.94117647, float(pm.average_parsed_ratio))

        # self.assertEqual(16.0/17.0, pm.average_parsed_ratio)

    # @unittest.skip
    def test_parse_postscript_alice_bug_001(self):
        """ test_parse_postscript """
        # print(__doc__, sys.stderr)

        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(alice_bug_001, options)

        self.assertEqual(15, len(tokens))

        for link in links:
            self.assertTrue(link[0]<15 and link[1]<15, str(link))

        # self.assertEqual(["most", "people", "start", "at", "our", "web", "site", "which", "has", "the", "main", "pg",
        #                   "search", "facility:"], tokens)

    def test_parse_postscript_alice_bug_002(self):
        """ Gutenberg Children bug test """
        options = 0
        # options |= (BIT_RWALL | BIT_CAPS)
        options &= ~BIT_STRIP

        tokens, links = parse_postscript(alice_bug_002, options)

        self.assertEqual(29, len(tokens), tokens)


    def test_get_link_set(self):
        """ Test for link extraction according to set options """
        # post_all_walls = "[(LEFT-WALL)(Dad[!])(was.v-d)(not.e)(a)(parent.n)(before)(.)(RIGHT-WALL)]" \
        #                  "[[0 7 2 (Xp)][0 1 0 (Wd)][1 2 0 (Ss*s)][2 5 1 (Osm)][2 3 0 (EBm)]" \
        #                  "[4 5 0 (Ds**c)][5 6 0 (Mp)][7 8 0 (RW)]][0]"
        expected_set = {(1, 2), (2, 5), (2, 3), (4, 5), (5, 6)}
        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP | BIT_PARSE_QUALITY
        tokens, links = parse_postscript(self.post_all_walls, options)
        result_set = get_link_set(tokens, links, options)

        self.assertTrue(result_set == expected_set)

    def test_prepare_tokens_both_walls_period_no_options(self):
        """ Test for filtering token list according to set options """
        token_list = ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '.', '###RIGHT-WALL###']
        token_list_no_walls = ['dad', 'was', 'not', 'a', 'parent', 'before', '.']
        token_list_no_period = ['###LEFT-WALL###', 'dad', 'was', 'not', 'a', 'parent', 'before', '###RIGHT-WALL###']
        token_list_words_only = ['dad', 'was', 'not', 'a', 'parent', 'before']

        # Should take no action
        options = 0 | BIT_RWALL
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list, result_list, "Lists are not the same!!!")

        # Should return a list with no walls only word-tokens and period
        options = 0 | BIT_NO_LWALL
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_no_walls, result_list, "Lists are not the same!!!")

        # Should return a list with walls, word-tokens and period
        options = 0 | BIT_RWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_no_period, result_list, "Lists are not the same!!!")

        # Should return a list with no walls and no period
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(token_list, options)
        self.assertEqual(token_list_words_only, result_list, "Lists are not the same!!!")

        tokens_period_in_brackets = ["dad", "[has]", "[a]", "[telescope]", "[.]"]
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(tokens_period_in_brackets, options)
        self.assertEqual(["dad", "[has]", "[a]", "[telescope]"], result_list, "Lists are not the same!!!")

        tokens_only_period_unboxed = ["[dad]", "has", "[binoculars]", "."]
        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(tokens_only_period_unboxed, options)
        self.assertEqual(["[dad]", "has", "[binoculars]"], result_list, "Lists are not the same!!!")

        seven_dots = ['###LEFT-WALL###', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '###RIGHT-WALL###']
        options = 0
        result_list = prepare_tokens(seven_dots, options)
        self.assertEqual(['###LEFT-WALL###', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]', '[.]'], result_list, "Lists are not the same!!!")

        options = 0 | BIT_NO_LWALL | BIT_NO_PERIOD
        result_list = prepare_tokens(seven_dots, options)
        self.assertEqual(['[.]', '[.]', '[.]', '[.]', '[.]', '[.]'], result_list, "Lists are not the same!!!")

    def test_skip_command_response(self):
        with open("tests/test-data/raw/debug-msg.txt") as file:
            text = file.read()

        pos = skip_command_response(text)

        # print(text[pos:], sys.stderr)
        self.assertEqual(175, pos)

    def test_skip_linkage_header(self):
        pos, err = skip_linkage_header(timeout_linkage)
        print(timeout_linkage[pos:])
        self.assertEqual(219, pos)
        self.assertEqual(PS_PANIC_DETECTED|PS_TIMEOUT_EXPIRED, err)

    def test_skip_linkage_header_explosion(self):
        pos, err = skip_linkage_header(explosion_no_linkages)
        print(explosion_no_linkages[pos:])
        # self.assertEqual(len(explosion_no_linkages), pos)
        self.assertEqual(-1, pos)
        self.assertEqual(PS_PANIC_DETECTED|PS_TIMEOUT_EXPIRED, err)
        # self.assertTrue(err)

    @unittest.skip
    def test_parse_postscript_explosion_no_linkages(self):

        options = BIT_NO_LWALL | BIT_NO_PERIOD | BIT_STRIP

        tokens, links = parse_postscript(explosion_no_linkages.replace("\n", ""), options)

        print(tokens)
        print(links)

        self.assertEqual(27, len(tokens))
        self.assertEqual(0, len(links))

    def test_get_linkage_cost(self):
        linkage = \
"""
        Linkage 1, cost vector = (UNUSED=0 DIS=-0.61 LEN=16)
[(LEFT-WALL)(the)(old.a)(beast.n)(was.v-d)(whinnying.v)(on)(his)(shoulder.n)(.)]
[[0 9 4 (Xp)][0 4 3 (WV)][0 3 2 (Wd)][3 4 0 (Ss*s)][1 3 1 (Ds**x)][2 3 0 (A)][4 6 1 (MVp)]
[4 5 0 (Ost)][5 6 0 (Mp)][6 8 1 (Js)][7 8 0 (Ds**c)]]
[0]
"""
        lnk_no, lnk_cost = get_linkage_cost(linkage)

        # print(f"Linkage #{lnk_no}, cost = {lnk_cost}", file=sys.stderr)

        self.assertEqual(1, lnk_no)
        self.assertEqual((0, Decimal("-0.61"), 16), lnk_cost)


if __name__ == '__main__':
    unittest.main()
