"""
Run this script directly after 'python3 manage.py migrate'.
"""
from os import path, environ
from datetime import datetime
from tensorflow.keras import Sequential, layers, Model
from django.db.utils import OperationalError
import django

from dotenv import load_dotenv

load_dotenv()

environ.setdefault("DJANGO_SETTINGS_MODULE", "schoolnn_app.settings")

django.setup()
from schoolnn.dataset import zip_to_full_dataset  # noqa: E402
from schoolnn.models import (  # noqa: E402
    Dataset,
    Architecture,
    TrainingParameter,
    Project,
    User,
    Workspace,
    TerminationCondition,
    LossFunction,
    Optimizer,
    AugmentationOptions,
)
from schoolnn.training import (  # noqa: E402
    WrappedArchitecture,
)


CAT_DOG_DATASET = "./cat_dog_dataset.zip"
MNIST_DATASET = "./minst.zip"


def get_cat_dog_solver() -> Model:
    model = Sequential()
    model.add(layers.Input(shape=(128, 128, 3)))
    model.add(
        layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    model.add(
        layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    model.add(
        layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    model.add(
        layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    model.add(layers.Dropout(0.4))
    model.add(layers.Flatten())
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(2, activation="softmax"))
    return model


def get_minst_solver() -> Model:
    model = Sequential()
    model.add(layers.Input(shape=(28, 28, 3)))
    # Conv
    model.add(
        layers.Conv2D(filters=256, kernel_size=(3, 3), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    # Conv
    model.add(
        layers.Conv2D(filters=128, kernel_size=(2, 2), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())
    # Conv
    model.add(
        layers.Conv2D(filters=128, kernel_size=(2, 2), activation="relu")
    )
    model.add(layers.MaxPool2D(pool_size=(2, 2)))
    model.add(layers.BatchNormalization())

    model.add(layers.Flatten())

    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(128, activation="relu"))
    model.add(layers.Dropout(0.4))
    model.add(layers.Dense(10, activation="softmax"))
    return model


def get_cat_dog_dataset(user: User) -> Dataset:
    if not path.isfile(CAT_DOG_DATASET):
        msg = "Erwartete Datei für Katzen-Hunde-Datensatz: {} nicht gefunden."
        print(msg.format(CAT_DOG_DATASET))
        quit()
    dataset = Dataset.objects.create(
        name="Katzen und Hunde",
        user=user,
        custom=False,
    )
    zip_to_full_dataset(open(CAT_DOG_DATASET, "rb"), dataset)
    return dataset


def cat_dog_project_setup(user: User):
    print("Erstelle DogCat Projekt")
    cat_dog_solver = get_cat_dog_solver()
    wrarch = WrappedArchitecture.from_keras_model(cat_dog_solver)

    arch = Architecture.objects.create(
        name="DogCat Solver Netz #1",
        user=user,
        custom=False,
        architecture_json=wrarch.to_dict(),
    )

    training_parameter = TrainingParameter(
        validation_split=0.1,
        learning_rate=0.001,
        termination_condition=TerminationCondition(seconds=600),
        batch_size=32,
        loss_function=LossFunction.CATEGORICAL_CROSSENTROPY,
        optimizer=Optimizer.ADAM,
        augmentation_options=AugmentationOptions.all_activated(),
    )

    print("Lade DogCat Datensatz")
    cat_dog_dataset = get_cat_dog_dataset(user)

    Project.objects.create(
        name="DogCat Solver Projekt #1",
        dataset=cat_dog_dataset,
        user=user,
        architecture=arch,
        training_parameter_json=training_parameter.to_dict(),
    )
    print("Fertig")


def get_mnist_dataset(user: User) -> User:
    if not path.isfile(MNIST_DATASET):
        print(
            "Erwartete Datei für MNIST-Datensatz: {} nicht gefunden.".format(
                MNIST_DATASET
            )
        )
        quit()
    dataset = Dataset.objects.create(
        name="MNIST",
        user=user,
        custom=False,
    )
    zip_to_full_dataset(open(MNIST_DATASET, "rb"), dataset)
    return dataset


def mnist_project_setup(user: User):
    print("Erstelle MNIST Projekt")
    minst_solver = get_minst_solver()
    wrarch = WrappedArchitecture.from_keras_model(minst_solver)

    arch = Architecture.objects.create(
        name="MNIST Solver Netz #1",
        user=user,
        custom=False,
        architecture_json=wrarch.to_dict(),
    )

    training_parameter = TrainingParameter(
        validation_split=0.1,
        learning_rate=0.001,
        termination_condition=TerminationCondition(seconds=600),
        batch_size=32,
        loss_function=LossFunction.CATEGORICAL_CROSSENTROPY,
        optimizer=Optimizer.ADAM,
        augmentation_options=AugmentationOptions.all_activated(),
    )

    print("Lade MNIST Datensatz")
    mnist_dataset = get_mnist_dataset(user)

    Project.objects.create(
        name="MNIST Solver Projekt #1",
        dataset=mnist_dataset,
        user=user,
        architecture=arch,
        training_parameter_json=training_parameter.to_dict(),
    )
    print("Fertig")


@django.db.transaction.atomic()
def main():
    workspace = Workspace.objects.create(
        name="Workspace #1",
        settings_json="",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )
    user = User.objects.get(id=1)  # should be admin
    user.workspace = workspace
    user.save()
    mnist_project_setup(user)
    cat_dog_project_setup(user)


def try_main_and_quit_with_helpful_error_messages():
    try:
        main()
    except OperationalError as e:
        if "no such table" in str(e):
            print("Database error, table not existing.")
            print('Did you run "python3 manage.py migrate" yet?')
            quit()
        raise
    except User.DoesNotExist:
        print("Example projects will be assigned to the admin user (id = 1).")
        print("But there is no such user.")
        print('Did you run "python3 manage.py createsuperuser" yet?')
        quit()


if __name__ == "__main__":
    try_main_and_quit_with_helpful_error_messages()
