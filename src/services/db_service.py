import logging
from typing import Union, List

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload


from src.core.config import settings
from src.models import User, Coords, PerevalAdded, PerevalImages, Level
from src.schemas.submit import SubmitDataRequest, SubmitDataResponse, Status, CoordsSchema, ImageSchema, UserSchema, SimpleResponse, LevelSchema, \
    SubmitDataUpdateRequest

logger = logging.getLogger("my_app")


class SubmitService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_pereval(self, data: SubmitDataRequest, user: User) -> Union[SubmitDataResponse, SimpleResponse]:
        """Создание нового перевала с координатами и изображениями."""
        try:
            query = select(PerevalAdded).where(PerevalAdded.title == data.title)
            result = await self.db.execute(query)
            existing_pereval = result.scalars().first()

            if existing_pereval:
                # Генерируем ссылку на существующий перевал
                share_link = f"http://{settings.app_host}:{settings.app_port}/submit/get/{existing_pereval.id}"

                # Возвращаем SimpleResponse с нужными данными
                return SimpleResponse(
                    state=0,
                    message=f"Перевал с названием '{data.title}' уже существует!",
                    share_link=share_link
                )

            # Проверка на существование координат с такими же значениями
            coords_query = select(Coords).where(
                Coords.latitude == data.coords.latitude,
                Coords.longitude == data.coords.longitude,
                Coords.height == data.coords.height
            )
            coords_result = await self.db.execute(coords_query)
            existing_coords = coords_result.scalars().first()

            if existing_coords:
                # Ищем перевал, который связан с найденными координатами
                pereval_query = select(PerevalAdded).where(PerevalAdded.coord_id == existing_coords.id)
                pereval_result = await self.db.execute(pereval_query)
                existing_pereval = pereval_result.scalar_one_or_none()  # Получаем первый перевал (если есть)

                if existing_pereval:
                    return SimpleResponse(
                        state=0,
                        message="Перевал с такими координатами уже существует.",
                        share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{existing_pereval.id}"
                    )

            # Если координаты не существуют, создаем новые
            coords = Coords(
                latitude=data.coords.latitude,
                longitude=data.coords.longitude,
                height=data.coords.height
            )
            self.db.add(coords)
            await self.db.flush()

            logger.info("Создание записи уровня сложности")
            level = Level(
                winter=data.level.winter,
                summer=data.level.summer,
                autumn=data.level.autumn,
                spring=data.level.spring
            )

            self.db.add(level)
            await self.db.flush()
            logger.info(f"Уровень сложности успешно добавлен с ID: {level.id}")

            # Создаем запись о перевале
            logger.info(f"Создание перевала: {data.title} для пользователя {user.email}")
            pereval = PerevalAdded(
                user_id=user.id,
                coord_id=coords.id,
                level_id=level.id,
                beauty_title=data.beauty_title,
                title=data.title,
                other_titles=data.other_titles,
                connect=data.connect,
                status=Status.new
            )
            self.db.add(pereval)
            await self.db.flush()

            # Сохраняем изображения
            images = []
            for img in data.images:
                image = PerevalImages(pereval_id=pereval.id, image_url=img.url, title=img.title)
                self.db.add(image)
                images.append(image)
            await self.db.flush()

            await self.db.commit()

            return SubmitDataResponse(
                message="Данные успешно отправлены",
                share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
                status=pereval.status,
                beauty_title=pereval.beauty_title,
                title=pereval.title,
                other_titles=pereval.other_titles,
                connect=pereval.connect,
                add_time=pereval.add_time,
                user=UserSchema(
                    fam=user.fam,
                    name=user.name,
                    otc=user.otc,
                    email=user.email,
                    phone=user.phone
                ),
                coords=CoordsSchema(
                    latitude=coords.latitude,
                    longitude=coords.longitude,
                    height=coords.height
                ),
                level=LevelSchema(
                    winter=level.winter,
                    summer=level.summer,
                    autumn=level.autumn,
                    spring=level.spring
                ),
                images=[ImageSchema(url=image.image_url, title=image.title) for image in images],
            )
        except Exception as e:
            await self.db.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    async def update_pereval_status(self, pereval_id: int, status: Status):
        """Обновление статуса перевала."""
        async with self.db.begin():
            query = select(PerevalAdded).where(PerevalAdded.id == pereval_id)
            result = await self.db.execute(query)
            pereval = result.scalar_one_or_none()

            if not pereval:
                raise HTTPException(status_code=404, detail="Перевал не найден")

            # Проверка, можно ли изменить статус
            if pereval.status in [Status.accepted, Status.rejected]:
                raise HTTPException(status_code=400, detail="Статус нельзя изменить после модерации")

            pereval.status = status
            await self.db.flush()

        return {"message": "Статус обновлен", "pereval_id": pereval.id, "status": pereval.status}

    async def get_pereval(self, pereval_id: int) -> SubmitDataResponse:
        """Получение перевала с пользователем, координатами и изображениями и сложностью."""
        query = select(PerevalAdded).options(
            joinedload(PerevalAdded.user),
            joinedload(PerevalAdded.coords),
            joinedload(PerevalAdded.level),
            joinedload(PerevalAdded.images)
        ).where(PerevalAdded.id == pereval_id)

        result = await self.db.execute(query)
        pereval = result.unique().scalar_one_or_none()

        if not pereval:
            raise HTTPException(status_code=404, detail="Перевал не найден")

        return SubmitDataResponse(
            message="Данные перевала",
            share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
            status=pereval.status,
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            add_time=pereval.add_time,
            user=UserSchema(
                fam=pereval.user.fam,
                name=pereval.user.name,
                otc=pereval.user.otc,
                email=pereval.user.email,
                phone=pereval.user.phone
            ),
            coords=CoordsSchema(
                latitude=pereval.coords.latitude,
                longitude=pereval.coords.longitude,
                height=pereval.coords.height
            ),
            level=LevelSchema(
                winter=pereval.level.winter,
                summer=pereval.level.summer,
                autumn=pereval.level.autumn,
                spring=pereval.level.spring
            ),
            images=[ImageSchema(url=image.image_url, title=image.title) for image in pereval.images],
        )

    async def get_all_perevals(self) -> List[SubmitDataResponse]:
        query = select(PerevalAdded).options(
            joinedload(PerevalAdded.user),
            joinedload(PerevalAdded.coords),
            joinedload(PerevalAdded.level),
            joinedload(PerevalAdded.images)
        )

        result = await self.db.execute(query)
        perevals = result.unique().scalars().all()  # Используем unique(), чтобы обработать коллекции корректно

        if not perevals:
            raise HTTPException(status_code=404, detail="Перевалы не найдены")

        return [SubmitDataResponse(
            message="Данные перевалов",
            share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
            status=pereval.status,
            beauty_title=pereval.beauty_title,
            title=pereval.title,
            other_titles=pereval.other_titles,
            connect=pereval.connect,
            add_time=pereval.add_time,
            user=UserSchema(
                fam=pereval.user.fam,
                name=pereval.user.name,
                otc=pereval.user.otc,
                email=pereval.user.email,
                phone=pereval.user.phone
            ),
            coords=CoordsSchema(
                latitude=pereval.coords.latitude,
                longitude=pereval.coords.longitude,
                height=pereval.coords.height
            ),
            level=LevelSchema(
                winter=pereval.level.winter,
                summer=pereval.level.summer,
                autumn=pereval.level.autumn,
                spring=pereval.level.spring
            ),
            images=[ImageSchema(url=image.image_url, title=image.title) for image in pereval.images],
        ) for pereval in perevals]

    async def update_pereval(self, pereval_id: int, data: SubmitDataUpdateRequest) -> SimpleResponse:
        """Обновление существующей записи перевала."""

        async with self.db.begin():
            # Получаем перевал по ID
            query = select(PerevalAdded).where(PerevalAdded.id == pereval_id)
            result = await self.db.execute(query)
            pereval = result.scalar_one_or_none()

            if not pereval:
                # Перевал не найден, возвращаем ошибку
                logger.error(f"Перевал с ID {pereval_id} не найден")
                return SimpleResponse(
                    state=0,
                    message="Перевал не найден",
                    share_link=""
                )

            logger.info(f"Перевал с ID {pereval_id} найден, статус: {pereval.status.value}")

            # Проверяем, можно ли редактировать запись (только если статус `new`)
            if pereval.status.value != "new":
                return SimpleResponse(
                    state=0,
                    message="Запись можно редактировать только в статусе new",
                    share_link=""
                )

            # Проверка на уникальность координат
            coords_query = select(Coords).where(
                Coords.latitude == data.coords.latitude,
                Coords.longitude == data.coords.longitude,
                Coords.height == data.coords.height
            )
            coords_result = await self.db.execute(coords_query)
            coords_list = coords_result.scalars().all()  # Получаем все результаты

            # Если найдены другие записи с такими же координатами, проверяем их
            if coords_list:
                for coord in coords_list:
                    # Исключаем проверку для перевала, который мы редактируем
                    if coord.id != pereval.coord_id:
                        # Получаем перевал, который использует эти координаты
                        related_pereval = await self.db.execute(
                            select(PerevalAdded).where(PerevalAdded.coord_id == coord.id)
                        )
                        related_pereval = related_pereval.scalar_one_or_none()

                        if related_pereval:
                            share_link = f"http://{settings.app_host}:{settings.app_port}/submit/get/{related_pereval.id}"
                            logger.error(f"Координаты {data.coords} уже заняты перевалом с ID {related_pereval.id}.")
                            return SimpleResponse(
                                state=0,
                                message="Координаты уже заняты другим перевалом",
                                share_link=share_link
                            )

            # Проверка на уникальность названия (title)
            title_query = select(PerevalAdded).where(PerevalAdded.title == data.title)
            title_result = await self.db.execute(title_query)
            title_list = title_result.scalars().all()

            if title_list:
                for title in title_list:
                    if title.id != pereval.id:
                        related_pereval = await self.db.execute(
                            select(PerevalAdded).where(PerevalAdded.title == title.title)
                        )
                        related_pereval = related_pereval.scalar_one_or_none()

                        if related_pereval:
                            share_link = f"http://{settings.app_host}:{settings.app_port}/submit/get/{related_pereval.id}"
                            logger.error(f"Перевал с названием {data.title} уже существует: ID {related_pereval.id}.")
                            return SimpleResponse(
                                state=0,
                                message="Перевал с таким названием уже существует",
                                share_link=share_link
                            )

            # Обновляем перевал
            pereval.beauty_title = data.beauty_title
            pereval.title = data.title
            pereval.other_titles = data.other_titles
            pereval.connect = data.connect

            # Обновляем координаты
            coords_query = select(Coords).where(Coords.id == pereval.coord_id)
            coords_result = await self.db.execute(coords_query)
            coords = coords_result.scalar_one_or_none()
            if coords:
                coords.latitude = data.coords.latitude
                coords.longitude = data.coords.longitude
                coords.height = data.coords.height

            # Обновляем уровень сложности
            level_query = select(Level).where(Level.id == pereval.level_id)
            level_result = await self.db.execute(level_query)
            level = level_result.scalar_one_or_none()
            if level:
                level.winter = data.level.winter
                level.summer = data.level.summer
                level.autumn = data.level.autumn
                level.spring = data.level.spring

            # Обновляем изображения, если переданы новые
            if data.images:
                delete_query = select(PerevalImages).where(PerevalImages.pereval_id == pereval.id)
                result = await self.db.execute(delete_query)
                old_images = result.scalars().all()
                for img in old_images:
                    await self.db.delete(img)

                for img in data.images:
                    new_image = PerevalImages(pereval_id=pereval.id, image_url=img.url, title=img.title)
                    self.db.add(new_image)

            await self.db.commit()

            logger.info(f"Перевал ID {pereval.id} успешно обновлен.")

            share_link = f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}"

            return SimpleResponse(
                state=1,
                message="Запись успешно обновлена",
                share_link=share_link
            )

    async def get_perevals_by_user_email(self, email: str):
        """Получить все перевалы, отправленные пользователем по email."""
        query = (
            select(PerevalAdded)
            .join(PerevalAdded.user)
            .options(
                joinedload(PerevalAdded.user),
                joinedload(PerevalAdded.coords),
                joinedload(PerevalAdded.level),
                joinedload(PerevalAdded.images)
            )
            .where(User.email == email)
        )

        result = await self.db.execute(query)
        perevals = result.unique().scalars().all()

        if not perevals:
            return []

        return [
            SubmitDataResponse(
                message="Данные перевала",
                share_link=f"http://{settings.app_host}:{settings.app_port}/submit/get/{pereval.id}",
                status=pereval.status,
                beauty_title=pereval.beauty_title,
                title=pereval.title,
                other_titles=pereval.other_titles,
                connect=pereval.connect,
                add_time=pereval.add_time,
                user=UserSchema(
                    fam=pereval.user.fam,
                    name=pereval.user.name,
                    otc=pereval.user.otc,
                    email=pereval.user.email,
                    phone=pereval.user.phone
                ),
                coords=CoordsSchema(
                    latitude=pereval.coords.latitude,
                    longitude=pereval.coords.longitude,
                    height=pereval.coords.height
                ),
                level=LevelSchema(
                    winter=pereval.level.winter,
                    summer=pereval.level.summer,
                    autumn=pereval.level.autumn,
                    spring=pereval.level.spring
                ),
                images=[ImageSchema(url=image.image_url, title=image.title) for image in pereval.images],
            )
            for pereval in perevals
        ]
