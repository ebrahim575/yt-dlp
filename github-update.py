import os

choice = input('pull or push? : ')
if choice == 'pull':
    os.system('git fetch')
    os.system('git pull')
elif choice == 'push':
    os.system('git add .')
    os.system('git commit -m "update"')
    os.system('git push')
else:
    print('Invalid choice')
