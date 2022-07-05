# impact-dao-alytics
Collection of scripts and notebooks for analyzing onchain DAO voting metrics using the [Snapshot GraphQL API](https://hub.snapshot.org/graphql/). 

## Caveats: 
- Not all DAOs use Snapshot for voting and not all DAOS that use Snapshot use it for all votes. (Tally is a widely used alternative.)
- Many DAOs use vote delegation. Voting powers represent delegated voting power, not necessarily tokens owned by that wallet.

## Getting started

1. Install requirements: `pip install -r requirements.txt`
2. Create a yaml file with the ENS addresses of DAOs you want to query. Example:

`daos: [ens.eth, gitcoindao.eth, aave.eth]`

3. Test/review the query parameters in the `get_proposals` and `get_votes` modules. Here's an example (you'll need to substitute the `$PROPOSAL` field with an actual proposal contract). 

```
 query Votes {
  votes (
    first: 10000
    where: {
      proposal: "$PROPOSAL"
    }
    orderBy: "vp",
    orderDirection: desc
  ) {
    id
    voter
    vp
    created
    choice
    space {
      id
    }
  }
}
```

## Execute the script

1. In the CLI, enter `python snapshot.py {YAML} {JSON}`
- The YAML file includes the list of DAOs as shown above
- The JSON file represents the outfile path that you want to dump all your data to

2. The script will execute, first grabbing all proposals for those DAOs and then getting votes for each proposal
3. The individual votes can take a while to process. The script provides updates every batch of 10 proposals.
4. You can add new proposals / DAOs by re-running the script. Old proposals are already serialized into the JSON file.

## Analyze results

The Jupyter notebook provides some initial analysis of:
- Total unique wallets / most active wallets
- Voter histograms
- DAO to DAO connections and network graphs
