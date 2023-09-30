import asyncio
import datetime

import aioschedule
from sqlalchemy import Column, String, Integer, Boolean, Date, create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE = "sqlite:///config.db"

Base = declarative_base()


class ChatConfig(Base):
    __tablename__ = 'chatconfig'
    chat_id = Column(Integer, primary_key=True)
    language = Column(String)
    bot_startup_time = Column(Integer)
    bot_endup_time = Column(Integer)
    status = Column(Boolean)


class Admin(Base):
    __tablename__ = 'admin'
    username = Column(String)
    user_id = Column(Integer, primary_key=True)
    date_append = Column(Date)
    super_admin = Column(Boolean)


# Database class for handling database operations
class Database:
    @staticmethod
    def get_current_hour():
        return datetime.datetime.now(datetime.timezone.utc).strftime("%H")

    def __init__(self):
        engine = create_engine(DATABASE, echo=False)
        Base.metadata.create_all(engine)
        session = sessionmaker(bind=engine)
        self.session = session()

    def sql_startup(self):
        if self.session:
            print('DB Connected True')

    def add_chat_to_config(self, data):
        new_chat = ChatConfig(
            chat_id=data['chat_id'],
            language=data['language'],
            bot_startup_time=data['bot_startup_time'],
            bot_endup_time=data['bot_endup_time'],
            status=data['status']
        )
        self.session.add(new_chat)
        self.session.commit()

    def delete_chat_from_config(self, chat_id):
        chat = self.session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        self.session.delete(chat)
        self.session.commit()

    def get_chat_status(self, chat_id):
        status = self.session.query(ChatConfig.status).filter_by(chat_id=chat_id).scalar()
        if status:
            return status
        return False

    def bot_reply_config(self, chat_id):
        config = self.session.query(ChatConfig).filter_by(chat_id=chat_id).first()
        if config:
            return config
        return False

    def status_falser(self, chat_id):
        chat = self.session.query(ChatConfig).filter_by(chat_id=chat_id)
        if chat.status:
            chat.status = False
            self.session.commit()

    def timer_true(self):
        dt = self.get_current_hour()
        chat_list = self.session.query(ChatConfig).filter_by(bot_startup_time=dt).all()
        for chat in chat_list:
            chat.status = True
        self.session.commit()

    def timer_false(self):
        if datetime.date.today().weekday() not in [5, 6]:
            time_now = self.get_current_hour()
            chat_list = self.session.query(ChatConfig).filter_by(bot_endup_time=time_now).all()
            for chat in chat_list:
                chat.status = False
            self.session.commit()

    async def run_scheduler(self):
        aioschedule.every().hours.at(":00").do(self.timer_true)
        aioschedule.every().hours.at(":00").do(self.timer_false)
        while True:
            await aioschedule.run_pending()
            await asyncio.sleep(60)

    messages = {'english': '🙌 Hi, I’m sorry, your manager isn’t available now. \n\n'
                           '🟢 You can contact the Support Team to solve your problem. Find the green viget at '
                           'the '
                           'platform (5:00-23:00 GMT daily) or email your question to help@datame.cloud. They '
                           'can fix the '
                           'majority of your issues.\n\n'
                           '🤖 Also, you can check your regional bot:\n'
                           '🇪🇸 @ad_velopment_bot.\n\n'
                           '👤 If you need your manager’s help exclusively, please wait for the answer during '
                           'the next '
                           'workday (Monday-Friday, ',

                'spanish': '🙌 Hola, lo siento, tu asesor no está disponible ahora.\n\n'
                           '🟢 Puedes contactar con el soporte para resolver tu duda vía el botón verde en la '
                           'plataforma '
                           '(1:00 - 19:00 UTC-5 cada día) o por el correo help@datame.cloud. Ellos pueden '
                           'ayudarte con '
                           'mayoría de los problemas.\n\n'
                           '🤖 Además puedes revisar el bot regional @ad_velopment_bot.\n\n'
                           '👤 Si tu pregunta es exclusivamente del dominio del CSM, por favor, espera la '
                           'respuesta '
                           'durante el próximo día laboral (Lunes-Viernes, ', }

    def make_admin_define(self, data):
        new_admin = Admin(
            username=data[1],
            user_id=data[2],
            date_append=datetime.datetime.utcnow().date(),
            super_admin=False
        )
        self.session.add(new_admin)
        self.session.commit()
        return True

    def make_super_admin_define(self, user_id):
        admin = self.session.query(Admin).filter_by(user_id=user_id).first()
        if admin:
            admin.super_admin = True
            self.session.commit()
            return True
        return False


db = Database()
