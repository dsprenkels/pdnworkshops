# pdnworkshops

`pdnworkshops` is a program made by [Radboud University's] [ru] / [Karpe Noktem's] [kn] weekend organising group _Pluk de Nacht_. It is used to determine the optimal distibution of a group of participants into different workshops, based on their preferences. This project is put on Github mainly for demonstrational purposes. It is not intended to be safe, so don't use it if you intend to expose it to the web.

[ru]: http://www.ru.nl/introductie/
[kn]: https://karpenoktem.nl/

## Setup

```shell
# install glpksol
sudo apt-get install glpk-utils

# create a virtualenv and install django 1.8
virtualenv pdn_virtualenv
source "pdn_virtualenv/bin/activate"
pip install --upgrade django==1.8
```

Check out `pdn/settings.py` to change settings like the database.

Then execute, in a shell:
```shell
python manage.py migrate          # set up the database
python manage.py createsuperuser  # create an admin user
```

## Usage

> At the moment, some settings are hardcoded into the model generation file
> `pdnworkshops/management/commands/calculate.py`. I reccommend reading it,
> before proceeding.

```shell
python manage.py runserver        # start the server
```

When your server is running, go to the admin panel (`http://localhost:8000/admin/`) and log in. You can now start adding workshops. When you are done adding workshops, your participants can start entering their preferences at `http://localhost:8000/`. Entered mistakes can easily be corrected using the admin panel.

When all preferences are entered, stop the server and go throught the following steps to get your solution.

```shell
# generate model.sol
python manage.py calculates

# optionally edit the model by hand
$EDITOR model.sol

# calculate the solution, this may take up a long time,
# depending on the problem
glpsol -m model.sol

# read the solution with some spreadsheet application
libreoffice solution.csv
```

## Additional rules

You may want to add additional rules. Below are some examples.

```ampl
# make sure nobody can do 'Vuurspuwen' in round 2 when they have drunk alcohol
# in round 1
subject to safety_first_contraint1{i in users}:
x[i,'Pils proeven',1] + x[i,'Vuurspuwen',2] <= 1;

# 'Nicole' is seventeen years old, so make sure she can't join the
# 'Pils proeven' (beer tasting) workshop
subject to alcohol_constraint1{r in rounds}:
x['Nicole','Pils proeven',r] = 0;

```

Add rules like these to `model.sol` before calling `glpsol` to add this rule to the model.

## Questions

Feel free to send me an email on my Github associated e-mail address.
