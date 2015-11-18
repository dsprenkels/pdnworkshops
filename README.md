# pdnworkshops

## setup

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

## using the program

> At the moment, some settings are hardcoded into the model generation file
> `pdnworkshops/management/commands/calculate.py`. I reccommend reading it,
> before proceeding.

```shell
python manage.py runserver        # start the server
```

When your server is running, go to the admin panel
(`http://localhost:8000/admin/`) and log in. You can now start adding
workshops. When you are done adding workshops, your participants can start
entering their preferences at `http://localhost:8000/`. Entered mistakes can
easily be corrected using the admin panel.

When all preferences are entered, stop the server and go throught the following
steps to get your solution.

```shell
# generate model.sol
python manage.py calculate

# optionally edit the model by hand
$EDITOR model.sol

# calculate the solution, this may take up a long time,
# depending on the problem
glpsol -m model.sol

# read the solution with some spreadsheet application
libreoffice solution.csv
```

## additional rules

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

Add rules like these to `model.sol` before calling `glpsol` to add this rule
to the model.
