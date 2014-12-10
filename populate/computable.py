__author__ = '2168879m'

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Spviz.scottviz.scottviz.settings")
from Spviz.scottviz.scottviz_app.models import *
from decimal import *
from data import number_of_msps, independent_parties

# the definitions here can be changed to get other statistics


def compute_division_turnout():
    divisions = Division.objects.all()
    msps = MSP.objects.all()

    # we have more msps in the db  (dead,resigned)
    error = len(msps) - number_of_msps

    # turnout for each division
    for division in divisions:
        absentVotes = Vote.objects.filter(division=division, vote=Vote.ABSENT)
        division.turnout = Decimal(number_of_msps - len(absentVotes)) * 100 /Decimal(number_of_msps)
        division.save()

def compute_msp_turnout():
    divisions = Division.objects.all()
    msps = MSP.objects.all()

    # turnout for each msps
    # computed over all divisions
    # one might want to compute it over the divisions on dates when the msp was a member
    # that would give more appropriate presence percentages
    # but not meaningful to compare with scatter
    for msp in msps:
        presentDivisions = len(divisions) - len(Vote.objects.filter(msp=msp, vote=Vote.ABSENT))
        msp.presence = presentDivisions * 100 / Decimal(len(divisions))
        msp.save()


def compute_division_rebels():
    divisions = Division.objects.all()

    # rebels for each division
    for division in divisions:
        division.rebels = len(Vote.objects.filter(division = division, rebellious = True))
        division.save()


def compute_msp_rebellions():
    divisions = Division.objects.all()
    msps = MSP.objects.all()

    # rebellions for each msp
    for msp in msps:
        # if msp.presence already computed :
        msp.rebellions = Decimal(len(Vote.objects.filter(msp=msp, rebellious=True)))*msp.presence/100
        msp.save()

        # otherwise, comment the previous 2 lines and uncomment the next 4 lines:
        #
        # votes_present = len(divisions) - len(Vote.objects.filter(msp=msp, vote=Vote.ABSENT))
        # if votes_present > 0 :
        #   msp.rebellions = Decimal(len(Vote.objects.filter(msp=msp, rebellious=True))) * 100 / Decimal(votes_present)
        # msp.save()

def independent_party_rebellious_votes(parties):

    # MSPs for independent cannot make rebellious votes
    votes = Vote.objects.all()
    for vote in votes:
        if vote.msp.party in parties:
            vote.rebellious = False
            vote.save()

            # alternative code that seems of greater complexity, maybe test for time?
    # for each vote for each msp for each independent party
    # for party in parties:
    #   party_msps = MSP.objects.filter(party = party)
    #   for msp in party_msps:
    #       votes = Vote.objects.all(msp = msp)
    #       for vote in votes:
    #           vote.rebellious = False
    #           vote.save()

# do not change, helper functions
def put(votes_list, party_vote, rebellious):
    for vote in votes_list:
        vote.party_vote = party_vote
        vote.rebellious = rebellious
        vote.save()

def not_independent_party_rebellious_votes(parties):

    divisions = Division.objects.all()
    # Check if a vote for msps in not independent parties is rebellious
    for party in parties:
        party_msps = MSP.objects.filter(party=party)
        threshold = (len(party_msps))/2
        for division in divisions:
            # get all the votes for this division
            division_votes = Vote.objects.filter(division=division)
            # split the votes by vote
            votes_yes = [vote for vote in division_votes.filter(vote=Vote.YES) if vote.msp in party_msps]
            votes_no = [vote for vote in division_votes.filter(vote=Vote.NO) if vote.msp in party_msps]
            votes_abstain = [vote for vote in division_votes.filter(vote=Vote.ABSTAIN) if vote.msp in party_msps]
            votes_absent = [vote for vote in division_votes.filter(vote=Vote.ABSENT) if vote.msp in party_msps]
            # decide a party vote if threshold reached
            # and put the results in
            if len(votes_yes)>threshold:
                put(votes_yes, Vote.YES, False)
                put(votes_no, Vote.YES, True)
                put(votes_abstain, Vote.YES, True)
                put(votes_absent,Vote.YES,False)
            elif len(votes_no)>threshold:
                put(votes_yes, Vote.YES, True)
                put(votes_no, Vote.YES, False)
                put(votes_abstain, Vote.YES, True)
                put(votes_absent,Vote.YES,False)
            elif len(votes_abstain)>threshold:
                put(votes_yes, Vote.ABSTAIN, True)
                put(votes_no, Vote.ABSTAIN, True)
                put(votes_abstain, Vote.ABSTAIN, False)
                put(votes_absent,Vote.ABSTAIN,False)
            else:
                put(votes_yes, Vote.ABSENT, False)
                put(votes_no, Vote.ABSENT, False)
                put(votes_abstain, Vote.ABSENT, False)
                put(votes_absent,Vote.ABSENT,False)

# DOES NOT WORK
# TO DO: FIX!
def compute_rebellious_votes():

    parties = Party.objects.all()

    # get a list of not independent parties:
    notindparties = parties
    for party in independent_parties:
        notindparties = notindparties.exclude(name__exact=party)
    # compute for not independent parties
    not_independent_party_rebellious_votes(notindparties)

    # get a list of independent parties
    indparties = parties
    for party in parties:
        indparties = indparties.exclude(id=party.id)
    # compute for independent parties
    independent_party_rebellious_votes(indparties)
