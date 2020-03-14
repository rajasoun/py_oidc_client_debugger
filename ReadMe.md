# Getting Started

In Terminal :

```
$ cp .env_template .env
```

Populate values for

* CLIENT_ID=
* CLIENT_SECRET=
* SCOPES=email openid profile
* AUTHORIZATION_BASE_URL=
* TOKEN_URL=
* USERINFO_URL=
* REDIRECT_URI=


```
$ docker-compose -f sso.yml build
$ docker-compose -f sso.yml up
```
