import sys
from copy import deepcopy

states = []

def readFile(filename):
    inputFile = open(filename, 'r')
    inputStrings = inputFile.readlines()
    inputStrings.pop(0)
    return inputStrings

class Team:
    def __init__(self, string):
        data = string.split()
        self.name = data[0]
        self.roundsPlayed = int(data[1])
        self.goalsOut = int(data[2])
        self.goalsIn = int(data[3])

    def canHavePlayed(self, team):
        return (self.goalsIn <= team.goalsOut) and (self.goalsOut <= team.goalsIn)

    def __repr__(self):
        return "(%s)\nRounds: %d\nGoalsOut: %d\nGoalsIn: %d\n" % (self.name, self.roundsPlayed, self.goalsOut, self.goalsIn)

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __deepcopy__(self, memo):
        return Team("%s %d %d %d" % (self.name, self.roundsPlayed, self.goalsOut, self.goalsIn))

def getData(filename):
    teamsData = readFile(sys.argv[1])
    return [Team(x) for x in teamsData]

def printMatches(matches):
    if not matches:
        print(matches)
        return
    for t, matched, i in matches:
        print("%s-%s %d-%d" %
              (t.name, matched[i].name, matched[i].goalsIn, matched[i].goalsOut))

def nextRound(matches):
    new_matches = deepcopy(matches)
    res = list()
    for team, matches, i in new_matches:
        team.goalsIn = team.goalsIn - matches[i].goalsOut
        team.goalsOut = team.goalsOut - matches[i].goalsIn
        if (team.goalsIn == team.goalsOut) or team.goalsIn < 0 or team.goalsOut < 0:
            return False
        team.roundsPlayed = team.roundsPlayed - 1
        res.append(team)
    return res

def matchesSort(x):
    return len(x[1])

def produceMatches(teams):
    knockedOut = [team for team in teams if team.roundsPlayed == 1]
    remained = [team for team in teams if team.roundsPlayed > 1]

    matchesFirstPass = list()
    for team in remained:
        matchesFirstPass.append((team, [x for x in knockedOut if x.canHavePlayed(team)]))

    matchesFirstPass = sorted(matchesFirstPass, key=matchesSort)

    error = False
    matches = list()
    for team, matched in matchesFirstPass:
        if len(matched) < 1:
            error = True
            break
        matches.append(
            (team, matched, -1))
    return (sorted(matches, key = matchesSort), error)

def cycleMatches(state):
    teams, matches_to_be_cycled, final_matches, to_be_cycled, end = state
        
    selected = set()
    for k in range(0, to_be_cycled):
        team, matched, i = matches_to_be_cycled[k]
        selected.add(matched[i])

    found = False
    team, matched, n = matches_to_be_cycled[to_be_cycled]

    for l in range(n+1, len(matched)):
        if matched[l] not in selected:
            selected.add(matched[l])
            matches_to_be_cycled[to_be_cycled] = (team, matched, l)
            found = True
            break

    if not found:
        selected.add(matched[n])

    for k in range(to_be_cycled + 1, len(matches_to_be_cycled)):
        team, matched, i = matches_to_be_cycled[k]
        for j in range(0, len(matched)):
            if matched[j] not in selected:
                selected.add(matched[j])
                matches_to_be_cycled[k] = (team, matched, j)
                break

    if end:
        to_be_cycled = to_be_cycled - 1
    else:
        to_be_cycled = to_be_cycled + 1

    if to_be_cycled > len(matches_to_be_cycled) - 1:
        to_be_cycled = to_be_cycled - 1
        end = True
    if to_be_cycled < 0:
        end = False

    return (teams, matches_to_be_cycled, final_matches, to_be_cycled, end)

def search(teams):

    matched, error = produceMatches(teams)
    state = cycleMatches((teams, matched, list(), 0, False))
    states.append(deepcopy(state))

    while True:
        while len(teams) > 2:
            
            teams, matched, final_matches, to_be_cycled, found = state

            final_matches = final_matches + matched
            
            teams = nextRound(matched)
            if (not teams):
                break
            matched, error = produceMatches(teams)

            if error or len(matched) < 2:
                break

            state = cycleMatches((teams, matched, final_matches, 0, False))
            states.append(deepcopy(state))

        # Exit Condition
        if teams != False:
            if len(teams) == 2:
                if teams[0].goalsIn == teams[1].goalsOut and teams[0].goalsOut == teams[1].goalsIn:
                    last = [(teams[0], [teams[1]], 0)]
                    return last + final_matches

        state = states.pop() # POP
        teams, matched, final_matches, to_be_cycled, found = state
            
        # If end of rounds and can't find match
        while not found and to_be_cycled < 0:
            state = states.pop() # POP
            teams, matched, final_matches, to_be_cycled, found = state

        teams, matched, final_matches, to_be_cycled, found = cycleMatches(state)
        states.append(deepcopy((teams, matched, final_matches, to_be_cycled, found)))

def main():
    if len(sys.argv) != 2:
        print("[Error] Invalid Arguments")

    teams = getData(sys.argv[1])
    matches = search(teams)

    printMatches(matches)


if __name__ == "__main__":
    main()
