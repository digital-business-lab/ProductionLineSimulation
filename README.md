# ProductionLineSimulation
In this repository we want to build a digital twin based on the dataflow of the machines.

# Setup
1. Pull the repository from github
```
git clone https://github.com/digital-business-lab/ProductionLineSimulation.git
```

2. Build and start the docker container (Docker Desktop has to run while doing this)
```
docker compose up -d --build
```

3. After the containers are running you have to open node-red and install the ui-dashboard package
- Open localhost:1880
- Go to the burger menu and click on "Palette verwalten" -> "Installationen" -> Install "node-red-dashboard"
- Then just double click on each node and click on "Fertig"
- The UI can be accessed via localhost:1880/ui

4. Start a machine or stop the machine by clicking the buttons. You can controll if its running by opening Grafana (localhost:3000) and look at the dashboard (Dashboards -> Postgres Table View). 

5. After you finished your work you can shut down the container by doing "docker compose down". If you want to restart it do "docker compose up -d". For restart and rebuild do step 2.

If machines do not work as intended you can look at the logs by doing "docker compose logs container-name"

# Contact
If you have any problems running the program or you find bugs, feel free to contact l.graf@oth-aw.de.