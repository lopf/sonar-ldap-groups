# Sonar LDAP/AD group synchronization

Synchronize LDAP/AD groups to Sonarqube. The official Sonarqube documentation includes this passage regarding delegation of authorization: _For the delegation of authorization, groups must be first defined in SonarQube._ The script aims to provide a solution to this.

Official Sonarqube documentation: https://docs.sonarqube.org/7.6/instance-administration/delegated-auth/

Sonarqube (https://www.sonarqube.org/) has great LDAP integration for user account. It lets you delegate authentication to an LDAP server such as a Microsoft Active Directory. If an LDAP user logs into Sonar, a local record is being created. If the LDAP/AD groups are synchronized to Sonar, we can set permissions for these groups to projects.

## Getting Started

### Prerequisites

The script was tested using Python 3.7 and Sonarqube 7.6 as target. In addition, a few PIP packages need to be present:
```
pip install -r requirements.txt
```

Generate a token for a user in the *sonar-administrators* group:

*Administration* --> *Security* --> *Users* in the *Tokens* column, click and generate a token.

### Configuration

See `./group-sync.py --help` for available parameters.

1. Copy the sample config into `config.yml` and adapt it to your environment
```
cp config.yml.sample config.yml
# edit config.yml
```
2. Run with no parameter to see how many groups would get created/deleted.
3. Execute with `--no-dry ` to actually create/delete the groups.

## Deployment

You may want to put this into a cronjob to run regularly.

Will provide Dockerfile soon...
Will provide K8s resources soon...

