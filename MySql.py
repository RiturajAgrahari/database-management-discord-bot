import discord
import mysql.connector
from discord import ui
from discord.ui import Button, View
from tabulate import tabulate


f = open("setup.txt", "rt")
HOST = f.readline()
USER = f.readline()
PASSWORD = f.readline()
f.close()


async def open_mysql(host=HOST, user=USER, password=PASSWORD):
    mydb = mysql.connector.connect(
        host=host,
        user=user,
        password=password,
    )
    return mydb


async def setup_database(message, interaction):
    exist = await check_setup_existence()

    if exist:
        msg = 'MySql is already set up earlier do you want to change it?'
        label = 'Remove Old MySql'
    else:
        msg = 'Set up your MySql now!'
        label = 'Setup New MySql'

    class MyView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label=label, style=discord.ButtonStyle.green)
        async def setup(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.message.delete()
            if exist:
                await authenticate_user(interaction, message)
            else:
                await setting_up_database(interaction)

    embed = discord.Embed(
        title='Setup',
        description=msg,
        color=discord.Color.dark_gray()
    )

    view = MyView()
    if interaction:
        view.response = await interaction.response.send_message(embed=embed, view=view)
    else:
        view.response = await message.channel.send(embed=embed, view=view)


async def setting_up_database(interaction):
    class MyModal(discord.ui.Modal, title="Setting up MySql!"):
        host = ui.TextInput(label='Host', placeholder="Enter your host name...", style=discord.TextStyle.short)
        user = ui.TextInput(label="User", placeholder="Enter your user...", style=discord.TextStyle.short)
        password = ui.TextInput(label="Password", placeholder="Enter your password...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> host = {self.host}, user = {self.user}, password = {self.password}')
            try:
                mydb = await open_mysql(str(self.host), str(self.user), str(self.password))
                mycursor = mydb.cursor()
                sql = 'show databases'
                mycursor.execute(sql)
                table = mycursor.fetchall()
                mydb.commit()
                await store_credentials(str(self.host), str(self.user), str(self.password))
                await interaction.response.send_message('Set up successful!', ephemeral=True)
            except Exception as e:
                print(e)
                await interaction.response.send_message('Invalid Credential!', ephemeral=True)

    await interaction.response.send_modal(MyModal())


async def store_credentials(host, user, password):
    fs = open("setup.txt", "w")
    fs.write(f"{host}\n{user}\n{password}")
    fs.close()


async def check_setup_existence():
    # READING LINES IN TEXT FILE
    setup_file = open("setup.txt", "rt")
    # print(setup_file.readline())
    exist = bool(setup_file.readline())
    # print(exist)
    setup_file.close()
    return exist


async def authenticate_user(interaction, message):
    class MyModal(discord.ui.Modal, title="Authenticate!"):
        password = ui.TextInput(label='Password', placeholder="Enter your old MySql password...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> password = {self.password}')
            a = open("setup.txt", "rt")
            host = a.readline()
            user = a.readline()
            old_password = a.readline().strip('\n')
            print(old_password)
            f.close()
            if str(old_password) == str(self.password):
                m = open("setup.txt", "w")
                m.write("")
                m.close()
                await setup_database(message, interaction)
            else:
                await interaction.response.send_message('Incorrect Password', ephemeral=True)

    await interaction.response.send_modal(MyModal())


async def update_mysql(interaction):
    class MyModal(discord.ui.Modal, title="Setting up new MySql!"):
        host = ui.TextInput(label='Host', placeholder="Enter your host name...", style=discord.TextStyle.short)
        user = ui.TextInput(label="User", placeholder="Enter your user...", style=discord.TextStyle.short)
        password = ui.TextInput(label="Password", placeholder="Enter your password...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> host = {self.host}, user = {self.user}, password = {self.password}')
            try:
                mydb = await open_mysql(str(self.host), str(self.user), str(self.password))
                mycursor = mydb.cursor()
                sql = 'show databases'
                mycursor.execute(sql)
                table = mycursor.fetchall()
                mydb.commit()
                await store_credentials(str(self.host), str(self.user), str(self.password))
                await interaction.response.send_message('Set up successful!', ephemeral=True)
            except Exception as e:
                print(e)
                await interaction.response.send_message('Invalid Credential!', ephemeral=True)

    await interaction.response.send_modal(MyModal())


async def security_msg(message):
    embed = discord.Embed(
        title='Authentication',
        description="You have to authenticate before accessing the database",
        color=discord.Color.red()
    )

    class MyView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label='Authenticate', style=discord.ButtonStyle.red)
        async def secure(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.message.delete()
            print(f'[MySql.py--31--] {interaction.user} : Authenticating...', end=' ')
            await security_check(interaction, message)

    view = MyView()
    view.response = await message.channel.send(embed=embed, view=view)


async def security_check(interaction, message):
    class MyModal(discord.ui.Modal, title="Authentication"):
        password = ui.TextInput(label="Password", placeholder="Enter your password...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> PASS = {self.password}')
            if str(self.password) == str(PASSWORD):
                print(f'Authentication SUCCESSFULL!')
                await start_mysql(interaction, message)
            else:
                print(f'PASS Authentication FAILED!')
                await interaction.response.send_message(f'Wrong Password', ephemeral=True)


    await interaction.response.send_modal(MyModal())


async def start_mysql(interaction, message):
    DB = await get_databases(message)
    Database = ''
    for i in range(0, len(DB)):
        Database += f'{DB[i][0]} \n'

    embed = discord.Embed(
        title='MySql',
        color=discord.Color.green()
    )
    embed.add_field(
        name='Databases',
        value=Database
    )

    class MyView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label='Use Database', style=discord.ButtonStyle.green)
        async def use_database(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--80--] {interaction.user} : show databases;')
            await interaction.message.delete()
            table = await get_databases(message)
            await show_databases(interaction, table, message)

        @discord.ui.button(label='Create Database', style=discord.ButtonStyle.blurple, disabled=True)
        async def create_database(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--87--] {interaction.user} : Database Creation Authentication...', end=' ')
            await interaction.message.delete()
            await create_authentication(interaction, message)

        @discord.ui.button(label='Close', style=discord.ButtonStyle.gray)
        async def close(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.message.delete()


    view = MyView()
    view.response = await interaction.response.send_message(embed=embed, view=view)


async def show_databases(interaction, table, message):
    class SelectMenu(discord.ui.Select):
        def __init__(self):
            options = []
            for i in range(0, len(table)):
                options.append(discord.SelectOption(label=table[i][0]))
            super().__init__(placeholder='Select Database:', options=options, min_values=0, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            print(f'[MySql.py--104--] {interaction.user} : {self.values[0]} - ')
            await interaction.message.delete()
            await use_database(interaction, self.values[0], message)

    class Select(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(SelectMenu())

    await interaction.response.send_message(content="Choose DATABASE", view=Select())


async def use_database(interaction, database, message):
    print(f'{message.author} : Checking table list!')
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    Table = await get_tables(database)
    Tables = ''
    for i in range(0, len(Table)):
        Tables += f'{Table[i][0]} \n'

    embed = discord.Embed(
        title='Database',
        description=database,
        color=discord.Color.green()
    )
    embed.add_field(
        name='Tables',
        value=Tables
    )

    class MyView(View):
        def __init__(self):
            super().__init__()

        @discord.ui.button(label='Back', style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--146--] {interaction.user} : -------BACK-------')
            await interaction.message.delete()
            await start_mysql(interaction, message)

        if len(Table) == 0:
            @discord.ui.button(label='No Table', style=discord.ButtonStyle.gray, disabled=True)
            async def use_table(self, interaction: discord.Interaction, button: discord.ui.Button):
                await interaction.message.delete()
        else:
            @discord.ui.button(label='Use Table', style=discord.ButtonStyle.green, disabled=False)
            async def use_table(self, interaction: discord.Interaction, button: discord.ui.Button):
                print(f'[MySql.py--157--] {interaction.user} : show tables;')
                await interaction.message.delete()
                await show_table(interaction, message, database)

        @discord.ui.button(label='Create Table', style=discord.ButtonStyle.blurple, disabled=True)
        async def create_table(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'Creating database : {message.author}')
            await interaction.message.delete()

        @discord.ui.button(label='Delete Database', style=discord.ButtonStyle.red, disabled=True)
        async def delete_database(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--168--] {interaction.user} : Database Deletion Authentication...', end=' ')
            await interaction.message.delete()
            await delete_authentication(interaction, message, database)



    view = MyView()
    view.response = await message.channel.send(embed=embed, view=view)


async def delete_authentication(interaction, message, database):
    class MyModal(discord.ui.Modal, title=f"Deleting Database"):
        Database_name = ui.TextInput(label=f'{database}', placeholder="Confirm the name of database...", style=discord.TextStyle.short)
        deletion_key = ui.TextInput(label="Key", placeholder="Enter Deletion key...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> database_name = {self.Database_name} , KEY = {self.deletion_key}')
            if str(self.Database_name).lower() == database:
                if str(self.deletion_key) == '1111':
                    # await delete_database(str(self.Database_name).lower())
                    await start_mysql(interaction, message)
                    await interaction.followup.send(f'You have successfully deleted a {self.Database_name} database')
                    print(f'{self.Database_name} database is successfully deleted!')

                else:
                    print(f'Deletion Authentication failed! (Wrong KEY)')
                    await interaction.response.send_message(f'You entered wrong creation key\n'
                                                    f'contact bot admin to get the deletion key')
            else:
                print(f'Deletion Authentication failed! (Wrong NAME)')
                await interaction.response.send_message(f'You entered wrong name')

    await interaction.response.send_modal(MyModal())


async def create_authentication(interaction, message):
    class MyModal(discord.ui.Modal, title="Creating Database"):
        Database_name = ui.TextInput(label='Database name', placeholder="Enter the name of new database...", style=discord.TextStyle.short)
        Creation_key = ui.TextInput(label="Key", placeholder="Enter Creation key...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> database_name = {self.Database_name} , KEY = {self.Creation_key}')
            if str(self.Creation_key) == '1111':
                # await create_database(self.Database_name)
                await start_mysql(interaction, message)
                await interaction.followup.send(f'You have successfully created a {self.Database_name}'
                                                        f' database')
                print(f'{self.Database_name} database is successfully created!')

            else:
                print(f'Creation Authentication Failed! (Wrong KEY)')
                await start_mysql(interaction, message)
                await interaction.followup.send(f'You entered wrong creation key\n'
                                                        f'contact bot admin to get the creation key')

    await interaction.response.send_modal(MyModal())


# async def create_database(database):
#     mycursor = mydb.cursor()
#     sql = f"CREATE DATABASE {database};"
#     print(sql)
#     mycursor.execute(sql)
#     mydb.commit()


# async def delete_database(database):
#     mycursor = mydb.cursor()
#     sql = f"DROP DATABASE {database};"
#     print(sql)
#     mycursor.execute(sql)
#     mydb.commit()


async def get_databases(message):
    mydb = await open_mysql()
    mycursor = mydb.cursor()

    sql = (f'show databases')
    mycursor.execute(sql)

    table = mycursor.fetchall()
    mydb.commit()
    return table


async def show_table(interaction, message, database):
    table = await get_tables(database)
    class SelectMenu(discord.ui.Select):
        def __init__(self):
            options = []
            for i in range(0, len(table)):
                options.append(discord.SelectOption(label=table[i][0]))
            super().__init__(placeholder='Select Table:', options=options, min_values=0, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            print(f'[MySql.py--266--] {interaction.user} : {self.values[0]} - ')
            await interaction.message.delete()
            await use_table(database, self.values[0], message)

    class Select(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(SelectMenu())

    await interaction.response.send_message(content=f'Choose Table', view=Select())


async def get_tables(database):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = (f'show tables')
    mycursor.execute(sql)
    table = mycursor.fetchall()
    mydb.commit()
    return table


async def use_table(database, table, message):
    embed = discord.Embed(
        title='Database',
        description=database,
        color=discord.Color.green(),
    )
    embed.add_field(name='Table',
                    value=table,
                    inline=True)

    class MyView(View):
        def __init__(self):
            super().__init__()
            self.response = None

        @discord.ui.button(label='Back', style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--318--] {interaction.user} : -------BACK-------')
            await interaction.message.delete()
            await use_database(interaction, database, message)

        @discord.ui.button(label='Show data', style=discord.ButtonStyle.green)
        async def show(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'{message.author} : Checking {table} content!')
            await interaction.message.delete()
            await show_table_data(database, table, message)

        @discord.ui.button(label='Edit Table', style=discord.ButtonStyle.blurple, disabled=True)
        async def edit(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.message.delete()
            await editing_authentication(interaction, message, database, table)

    view = MyView()
    view.response = await message.channel.send(embed=embed, view=view)


async def delete_table(database, table):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = f"DROP TABLE {table};"
    print(sql)
    mycursor.execute(sql)
    mydb.commit()


async def clear_table(database, table, message):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    try:
        mycursor = mydb.cursor()
        sql = (f'truncate table {table}')

        mycursor.execute(sql)

        mydb.commit()
        await message.channel.send(f"all the values of '{table}' is cleared!")
    except Exception as e:
        await message.channel.send(f"Something went wrong!\n {e}")


async def show_table_data(database, table, message):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = (f'select * from {table}')

    mycursor.execute(sql)

    data = mycursor.fetchall()

    table_data = []

    column = await show_table_columns(database, table)
    head = []
    for c in range(0, len(column)):
        head.append(column[c][0])
    table_data.append(head)

    for i in range(0, len(data)):
        info = []
        for j in range(0, len(data[i])):
            info.append(data[i][j])
        table_data.append(info)

    table = tabulate(table_data, headers='firstrow')
    await message.channel.send(f'```\n{table}\n```')


async def add_column(interaction, database, table, message):
    class MyModal(discord.ui.Modal, title=f"Creating Column"):
        Column_name = ui.TextInput(label=f'Column name', placeholder="Write the column name...", style=discord.TextStyle.short)
        Datatype = ui.TextInput(label="Datatype", placeholder="Enter Datatype...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(self.Column_name, self.Datatype)
            await create_column(database, table, self.Column_name, self.Datatype)
            await use_table(database, table, message)
            await interaction.followup.send(f'You have successfully created a column of {self.Column_name}'
                                            f' name and {self.Datatype} datatype')

    await interaction.response.send_modal(MyModal())


async def create_column(database, table, column, datatype):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = (f'ALTER TABLE {table} ADD {column} {datatype};')
    mycursor.execute(sql)
    mydb.commit()


async def delete_column(interaction, database, table, message):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = (f'desc {table}')
    mycursor.execute(sql)
    column = mycursor.fetchall()
    print(column)
    # return column
    class SelectMenu(discord.ui.Select):
        def __init__(self):
            options = []
            for i in range(0, len(column)):
                options.append(discord.SelectOption(label=column[i][0]))
            super().__init__(placeholder='Select Table:', options=options, min_values=0, max_values=1)

        async def callback(self, interaction: discord.Interaction):
            await interaction.message.delete()
            await remove_column(database, table, self.values[0])
            await edit_table(interaction, message, database, table)


    class Select(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(SelectMenu())

    await interaction.response.send_message(content=f'Columns', view=Select())


async def remove_column(database, table, column):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )
    mycursor = mydb.cursor()
    sql = f'ALTER TABLE {table} DROP COLUMN {column};'
    mycursor.execute(sql)
    mydb.commit()


async def show_table_columns(database, table):
    mydb = mysql.connector.connect(
        host=HOST,
        user=USER,
        password=PASSWORD,
        database=database
    )

    mycursor = mydb.cursor()
    sql = (f'desc {table}')

    mycursor.execute(sql)

    column = mycursor.fetchall()
    return column


async def editing_authentication(interaction, message, database, table):
    class MyModal(discord.ui.Modal, title=f"Editing Authentication"):
        Table_name = ui.TextInput(label=f'{table}', placeholder="Confirm the name of Table...", style=discord.TextStyle.short)
        Editing_key = ui.TextInput(label="Key", placeholder="Enter Editing key...", style=discord.TextStyle.short)

        async def on_submit(self, interaction: discord.Interaction):
            print(f'INPUT --> database_name = {self.Table_name} , KEY = {self.Editing_key}')
            Table = str(self.Table_name).lower()
            if Table == table:
                if str(self.Editing_key) == '1111':
                    await edit_table(interaction, message, database, table)
                    await interaction.followup.send(f'Authentication Successfull!')
                    print(f'{self.Table_name} table --> Editing Authentication Successfull!')

                else:
                    print(f'Editing Authentication failed! (Wrong KEY)')
                    await interaction.response.send_message(f'You entered wrong editing key\n'
                                                            f'contact bot admin to get the deletion key')
            else:
                print(f'Editing Authentication failed! (Wrong NAME)')
                await interaction.response.send_message(f'You entered wrong name')

    await interaction.response.send_modal(MyModal())


async def edit_table(interaction, message, database, table):
    embed = discord.Embed(
        title='Database',
        description=database,
        color=discord.Color.green(),
    )
    embed.add_field(name='Table',
                    value=table,
                    inline=True)

    class MyView(View):
        def __init__(self):
            super().__init__()
            self.response = None

        @discord.ui.button(label='Back', style=discord.ButtonStyle.gray)
        async def back(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'[MySql.py--547--] {interaction.user} : -------BACK-------')
            await interaction.message.delete()
            await use_table(database, table, message)

        @discord.ui.button(label='Show data', style=discord.ButtonStyle.green)
        async def show(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'{message.author} : Checking {table} content!')
            await interaction.message.delete()
            await show_table_data(database, table, message)

        @discord.ui.button(label='Add Column', style=discord.ButtonStyle.green)
        async def add(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'{message.author} : Cleared all data of table - {table} from database - {database}')
            await interaction.message.delete()
            await add_column(interaction, database, table, message)

        @discord.ui.button(label='Clear Table data', style=discord.ButtonStyle.blurple)
        async def clear(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'{message.author} : Cleared all data of table - {table} from database - {database}')
            await interaction.message.delete()
            await clear_table(database, table, message)
            await edit_table(interaction, message, database, table)

        @discord.ui.button(label='Delete Column', style=discord.ButtonStyle.red)
        async def delete_column(self, interaction: discord.Interaction, button: discord.ui.Button):
            await interaction.message.delete()
            await delete_column(interaction, database, table, message)

        @discord.ui.button(label='Delete Table', style=discord.ButtonStyle.red)
        async def delete(self, interaction: discord.Interaction, button: discord.ui.Button):
            print(f'{message.author} : Trying to delete a {table}!')
            await interaction.message.delete()
            await delete_table(database, table)
            await use_database(interaction, database, message)

    view = MyView()
    view.response = await message.channel.send(embed=embed, view=view)

