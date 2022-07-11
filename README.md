# Hackathon

## Problem
The client wants to easily read the data about the virtual machines that their team is in managment of.
The data consists of the data and meta parts, meta isn't required for the information to be valid.

```json
data schema
{
    "vm_{{ number }}":
        {
            "username": "{{ name }}",
            "password": "{{ password }}",
            "host": "{{ host_ip }}",
            "interfaces": "{% interfaces %}",
            "services": "{% services %}",
            "meta": "{{ meta }}"
        },
    .
    .
    .
}
```

```json
meta schema
"meta":
    {
        "createdAt": "{{ creation_timestamp }}",
        "expirationDate":"{{ expiration_timestamp }}",
        "team": "{{ team }}",
        "art": "{{ art }}",
        "uuid": "{{ uuid }}"
    }
```

The identifier of the data that the client wants to read is the vm instance key (of the form vm_{{ number }}). The credentials should be decrypted unless the user doesn't provide a valid key then left encrypted. The interfaces should be posted with their respective ports. Only the machines with "terraform" service are of interest to the team, because they can be managed remotely.
If the data has meta available then the response to the client should start with:
```
    UUID: {{ uuid }},
    Created at: {{ createdAt }} with lease ending at {{ expirationDate }},
    Managed by {{ team }}
```

```
    The virtual machine {{ vm_<number> }} can be found under IP {{ host }}.
    Username and password required to login are: {{ username }} [{{ password }}].
    The interfaces that are available are: {% interfaces %}.
```

## Technical requirements
* The data should be provided to the client as fast as possible
* Reading of data can't take up more than 10 times the file size in RAM
* The user needs to be able to provide the input data (VM name)
* The data should be provided in the way that allows its transport (log file, database access, http server your choice)
* The input file is dynamic, the user may want to change it one day, don't hardcode!
* Remember that encryption key is considered vulnerable data, don't store it in a file like the client did ;)
* And last but not least the data is encrypted using python's Fernet, however there are solutions for the encryption in other languages, don't worry - sometimes it's better to use a ready solution that to write your own (http://amiteyal.com/?p=1956 f.e.)