#!/bin/bash
# Engine v0.2 + rules API acceptance test. Run in tmux; results in ~/engine-v2/t02.log (about 6 min)
export PATH="$HOME/bin:$PATH"; E=~/engine-v2; API=http://localhost:8000/api/v2
L=$E/engine.log; O=$E/t02.log; : > $O; touch $L
step(){ echo "=== $1" >> $O; }
grab(){ sleep "${1:-4}"; tail -n +$((MARK+1)) $L >> $O; MARK=$(wc -l < $L); }
waitfor(){ for i in $(seq 120); do tail -n +$((MARK+1)) $L | grep -q "$1" && break; sleep 2; done; grab 1; }
api(){ echo "\$ $1 $2" >> $O; curl -s -X "$1" "$API$2" -H 'Content-Type: application/json' ${3:+-d "$3"} >> $O; echo >> $O; }
step "rules written"; python3 $E/mkrule.py mix >> $O
MARK=$(wc -l < $L); simctl start >/dev/null; simctl side start >/dev/null; engctl start >/dev/null
step "A: expect test_bad rejected; NO START for test_skip or test_dates; test_sun START about 1 min in"
waitfor 'confirmed on'
step "B: unreadable rules.json: expect a problem line and NO END"
cp $E/rules.json $E/rules.good; echo '{' > $E/rules.json; grab 12
step "C: restored: expect the test_bad problem again and still NO END"
mv $E/rules.good $E/rules.json; grab 8
step "D: sun window ends about 3 min in: expect END and confirmed off"
waitfor 'confirmed off'
step "E: group rule: expect START, BOTH lights confirmed on"
python3 $E/mkrule.py group >> $O; waitfor 'side_deck_flood: confirmed on'
step "F: API status for the group rule and the group"
curl -s $API/status | python3 -c "import json,sys; s=json.load(sys.stdin); print('rule', s['rules'].get('test_group')); print('groups', s['groups']); print('sun', s['sun'])" >> $O
step "G: API STOP & SKIP TODAY: expect END and both lights off"
api POST /rules/test_group/skip-next; waitfor 'side_deck_flood: confirmed off'
step "H: API rejects a bad rule (expect 422 state must be on)"
api POST /rules '{"id":"x","targets":["front_door_flood"],"state":"off","start":{"clock":"06:00"},"end":{"clock":"07:00"}}'
step "I: API turns the rule off and back on"
api POST /rules/test_group/enabled '{"enabled":false}'; api POST /rules/test_group/enabled '{"enabled":true}'
engctl stop >/dev/null; simctl stop >/dev/null; simctl side stop >/dev/null; rm -f $E/rules.json $E/state.json
echo "=== DONE" >> $O
