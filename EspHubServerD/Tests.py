from Plots import DisplayPlot
from Scheduler import PeriodicDisplayTask
from django.core.management import call_command
import django
import os
import sys

# plot = DisplayPlot.DisplayPlot([1, 2, 3])
# img = plot.render_to_png()

# task = PeriodicDisplayTask.PeriodicDisplayTask()
# task.start()

print("start server")
sys.path.append('/WebUi')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'WebUi.settings')
django.setup()
call_command('runserver', use_reloader=False)
