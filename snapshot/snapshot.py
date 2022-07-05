import glob
import json
import requests
import sys
import yaml


global JSON_DATAPATH
global YMAL_PATH
JSON_DATAPATH = 'votes/voting_records.json'
YAML_PATH = 'daolist.yaml'

YAML_DAOLIST_IDENTIFIER = 'daos'

def get_proposals(list_of_daos):

    str_list = ", ".join(f'"{x}"' for x in list_of_daos)
    query = """
        query Proposals {
            proposals(
              first: 1000,
              skip: 0,
              where: {
                space_in: [$DAO_LIST],
                state: "closed"
              },
              orderBy: "created",
              orderDirection: desc
            ) {
              id
              title
              body
              choices
              start
              end
              snapshot
              state
              scores
              scores_by_strategy
              scores_total
              scores_updated
              author      
              space {
                id
                name
              }
            }
          }
    """
    query = query.replace("$DAO_LIST", str_list)
    url = 'https://hub.snapshot.org/graphql/'
    r = requests.post(url, json={'query': query})
    json_data = json.loads(r.text)
    proposals = json_data['data']['proposals']

    print(f"Successfully retrieved {len(proposals)} proposals from {len(list_of_daos)} DAOs.")

    return proposals


def get_votes(proposal_id):

    query = """
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
    """
    query = query.replace("$PROPOSAL", proposal_id)
    url = 'https://hub.snapshot.org/graphql/'
    
    r = requests.post(url, json={'query': query})
    json_data = json.loads(r.text)
    return json_data


    
def update_voting_records(proposal_id):

    with open(JSON_DATAPATH, 'r+') as json_file:
        try:
            data = json.load(json_file)
        except:
            data = []
            
        json_data = get_votes(proposal_id)
        data.append({
            'proposal': proposal_id, 
            'votes': json_data['data']['votes']
        })
        json_file.seek(0)
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':

    args = sys.argv

    if len(args) == 3:
        try:
            JSON_DATAPATH = args[2]
            if ".json" not in JSON_DATAPATH.lower():
                print("** Error **")
                print("Unable to open JSON file. Correct format is: python snapshot.py <YAML file> <JSON file>")
                exit()
        except Exception as ex:
            print("** Error **")
            print("Unable to open JSON file. Correct format is: python snapshot.py <YAML file> <JSON file>")
            print(str(ex))
            exit()
    
    if 2 <= len(args) <= 3:
        try:
            YAML_PATH = args[1].lower()
            if ".yaml" not in YAML_PATH.lower():
                print("** Error **") 
                print("Unable to open YAML file. Correct format is: python snapshot.py <YAML file>")
                exit()                
        except Exception as ex:
            print("** Error **") 
            print("Unable to open YAML file. Correct format is: python snapshot.py <YAML file>")
            print(str(ex))
            exit()


    y = yaml.load(open(YAML_PATH), Loader=yaml.FullLoader)
    if YAML_DAOLIST_IDENTIFIER not in y:
        print("** Error **")
        print(f"{YAML_DAOLIST_IDENTIFIER} is not present in the YAML file.")
        exit()

    dao_list = y[YAML_DAOLIST_IDENTIFIER]
    proposals = get_proposals(dao_list)

    if not glob.glob(JSON_DATAPATH):
        f = open(JSON_DATAPATH, "w+") 
        f.close() 
    try:
        with open(JSON_DATAPATH, 'r+') as json_file:
            data = json.load(json_file)
            if data:
                existing_proposals = [record['proposal'] for record in data]
                proposals = [p for p in proposals if p['id'] not in existing_proposals]
                print(f"Getting voting records for {len(proposals)} proposals.")
    except:
        pass

    for i,p in enumerate(proposals):
        if not i % 10:
            print(f"{i} of {len(proposals)}")
        update_voting_records(p['id'])