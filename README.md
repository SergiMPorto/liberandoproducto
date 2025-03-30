# Práctica de Monitorización con FastAPI, Prometheus, Grafana y CircleCI

## Lanzamiento de la aplicación

Lo primero que hicimos fue lanzar la aplicación.  
Una vez lanzada, creamos un nuevo endpoint:

```
/bye
```

![nuevo endpoint](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/metricas%20personalizadas%20para%20el%20nuevo%20endpoint.png)

---

## Test unitario del endpoint

Creamos un test para verificar que el nuevo endpoint devuelve un `status_code` 200 y el `json` esperado.

![pruebas unitarios nuevo endpoint](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/testunitarionuevoendpoint.png)

---

## Helm Chart personalizado

Creamos un chart llamado `fastapi-chart` con los distintos templates necesarios:

- `deployment.yaml`
- `service.yaml`
- `servicemonitor.yaml`
- `stress-cpu.yaml`
- `values.yaml`

Entre ellos, el más relevante es el `ServiceMonitor`, que le indica a Prometheus qué servicio debe monitorear. Este conecta un `Service` de Kubernetes con Prometheus:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: {{ .Release.Name }}-servicemonitor
  labels:
    release: monitoring
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: {{ .Chart.Name }}
      app.kubernetes.io/instance: {{ .Release.Name }}
  endpoints:
    - port: metrics  
      path: /metrics
      interval: 15s
  namespaceSelector:
    matchNames:
      - fast-api
```

---

## CI/CD con CircleCI

Creamos un pipeline para lanzar los tests y subir la imagen a DockerHub al hacer push con una versión `tag`.

```yaml
version: 2.1

executors:
  python_executor:
    docker:
      - image: cimg/python:3.11
    working_directory: ~/project

jobs:
  test:
    executor: python_executor
    steps:
      - checkout
      - run:
          name: Upgrade pip
          command: pip install --upgrade pip
      - run:
          name: Install dependencies
          command: pip install -r requirements.txt
      - run:
          name: Run unit tests with coverage
          command: pytest --cov

  build-and-push:
    executor: python_executor
    steps:
      - checkout
      - setup_remote_docker:
          docker_layer_caching: true
      - run:
          name: Unshallow git repo
          command: git fetch --prune --unshallow || true
      - run:
          name: Set VERSION env from tag
          command: echo "export VERSION=${CIRCLE_TAG#v}" >> $BASH_ENV

workflows:
  version: 2
  ci:
    jobs:
      - test:
          filters:  
            branches:
              ignore: /.*/
            tags:
              only: /^v.*/
      - build-and-push:
          requires:
            - test
          filters:
            branches:
              ignore: /.*/
            tags:
              only: /^v.*/
```
![creando versiones](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/crearlasversiones.png)
![CIrcleCi](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/circlecicorrecto.png)

---

## Métricas del endpoint

Creamos un contador Prometheus para medir cuántas veces se llama al nuevo endpoint `/bye`.



![prueba navegador](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/pruebaendpoindnavegador.png)
![contador de métricas](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/contador%20metricas.png)


---

## Monitorización con Prometheus

Desplegamos Prometheus con Helm sobre Minikube y lo configuramos con `kube-prometheus-stack`.

![ despliegue de Prometheus](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/desplegar%20prometeo.png)

---

## Alertas con PrometheusRule

Creamos reglas de alerta para:

- Peticiones excesivas al endpoint `/bye`
- Consumo de CPU elevado

![PrometheusRule](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/prometheusrules.png)

---

## Notificaciones en Slack

Configuramos Alertmanager para que envíe alertas a un canal de Slack. 


![configuración de Slack](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/configurandoslack.png)

---

## Generación manual de alertas

Probamos a generar manualmente alertas:

- Lanzando múltiples peticiones al endpoint `/bye`  
- Saturando la CPU con `threading` en Python (no conseguimos superarlo aunque se probó con múltiples hilos y configuraciones)

![firing de la alerta del endpoint](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/alertaactivasa.png)
![alerta en stack](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/alertaenstackdettomanybyeresquest.png)

---

## Dashboard en Grafana

Creamos un dashboard en Grafana (importando JSON) para visualizar el número de veces que se ha llamado al endpoint `/bye`.

![panel de llamadas en Grafana](https://github.com/SergiMPorto/liberandoproducto/blob/main/images/grafanabyllamadas.png)
