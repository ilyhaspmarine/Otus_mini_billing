# Домашнее задание №7
## Restfull

### Сервис биллинга
#### Функционал
- Создание нового кошелька для пользователя (1 кошелек на пользователя)
- Проведение операций по кошельку (в + или в -)
- Получение текущего баланса кошелька

### ПОДГОТОВКА
#### в /etc/hosts прописываем
```
127.0.0.1 arch.homework 
```

#### Запускаем docker
любым вариантом, у меня docker desktop с виртуализацией VT-d

#### Запускаем minikube
```
minikube start --driver=docker
```

#### NGINX
Считам, что с прошлых дз он всё ещё в кластере


### СТАВИМ ПРИЛОЖЕНИЕ
#### Создаем namespace под сервис аутентификации
```
kubectl create namespace billing
```

#### "Внешняя" поставка секретов в кластер
##### Секрет с данными для подключения к БД
```
kubectl apply -f ./secret/billing_secret.yaml -n billing
```

#### Переходим в директорию с чартом
```
cd ./billing-app
```

#### Загружаем чарты зависимостей
```
helm dependency update
```

#### Возвращаемся в корень
```
cd ../
```

#### Устанавливаем чарт сервиса
```
helm install billing billing-app -n billing
```

#### Включаем (и не закрываем терминал)
```
minikube tunnel
```

#### Проверяем health-check (в новом окне терминала)
```
curl http://arch.homework/billing/health/
```


### КАК УДАЛИТЬ ПРИЛОЖЕНИЕ
#### Удаляем чарт и БД
```
helm uninstall billing -n billing
```

#### Удаляем секрет
```
kubectl delete secret billing-db-secret -n billing
```

#### Удаляем PVC, оставшиеся от БД
```
kubectl delete pvc -l app.kubernetes.io/name=billing-postgresql,app.kubernetes.io/instance=billing -n billing
```

#### Сносим PV, оставшиеся от БД (если reclaimPolicy: Retain)
```
kubectl get pv -n billing
```
Смотрим вывод, узнаем <имя PV> (к сожалению, меток у него не будет - я проверил)
```
kubectl delete pv <имя PV> -n billing
```

### Готово!