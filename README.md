# Práctica de Monitorización con FastAPI, Prometheus, Grafana y CircleCI

## Lanzamiento de la aplicación

Lo primero que hicimos fue lanzar la aplicación.  
Una vez lanzada, creamos un nuevo endpoint:

```
/bye
```

[Insertar imagen del nuevo endpoint]

---

## Test unitario del endpoint

Creamos un test para verificar que el nuevo endpoint devuelve un `status_code` 200 y el `json` esperado.

[Insertar imagen del test unitario]

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

[Insertar imagen del pipeline funcionando]

---

## Métricas del endpoint

Creamos un contador Prometheus para medir cuántas veces se llama al nuevo endpoint `/bye`.

[Insertar imagen con prueba de métricas]

---

## Monitorización con Prometheus

Desplegamos Prometheus con Helm sobre Minikube y lo configuramos con `kube-prometheus-stack`.

[Insertar imagen del despliegue de Prometheus]

---

## Alertas con PrometheusRule

Creamos reglas de alerta para:

- Peticiones excesivas al endpoint `/bye`
- Consumo de CPU elevado

[Insertar imagen del archivo PrometheusRule]

---

## Notificaciones en Slack

Configuramos Alertmanager para que envíe alertas a un canal de Slack. 

[Insertar imagen de configuración de Slack]

---

## Generación manual de alertas

Probamos a generar manualmente alertas:

- Lanzando múltiples peticiones al endpoint `/bye`  
- Saturando la CPU con `threading` en Python (no conseguimos superarlo aunque se probó con múltiples hilos y configuraciones)

[Insertar imagen del firing de la alerta del endpoint]

---

## Dashboard en Grafana

Creamos un dashboard en Grafana (importando JSON) para visualizar el número de veces que se ha llamado al endpoint `/bye`.

[Insertar imagen del panel de llamadas en Grafana]