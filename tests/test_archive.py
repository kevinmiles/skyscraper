import tempfile
import datetime
import time
import os
import gzip

import skyscraper.archive


def write_file_with_date(f, content, datetime):
    f.write(content.encode('utf-8'))
    f.seek(0)

    f_time = time.mktime(datetime.timetuple())
    os.utime(f.name, (f_time, f_time))


def test_archive_old_files(tmpdir):
    with tempfile.NamedTemporaryFile(dir=tmpdir) as f_1, \
            tempfile.NamedTemporaryFile(dir=tmpdir, delete=False) as f_21, \
            tempfile.NamedTemporaryFile(dir=tmpdir, delete=False) as f_22, \
            tempfile.NamedTemporaryFile(dir=tmpdir, delete=False) as f_3:

        today = datetime.datetime.today()
        this_month_file = today.strftime('%Y-%m.jl.gz')
        # use 28, because the shortest month is 28 days. Jumping 30 days back
        # we might possibly get a date from January if it's March 1st
        last_month = datetime.datetime(today.year, today.month, 15) \
            - datetime.timedelta(days=28)
        last_month_file = last_month.strftime('%Y-%m.jl.gz')
        two_months_ago = datetime.datetime(today.year, today.month, 15) \
            - datetime.timedelta(days=56)
        two_months_ago_file = last_month.strftime('%Y-%m.jl.gz')

        write_file_with_date(f_1, '{"foo": "data_1"}', today)
        write_file_with_date(f_21, '{"foo": "data_21"}', last_month)
        write_file_with_date(f_22, '{"foo": "data_22"}', last_month)
        write_file_with_date(f_3, '{"foo": "data_3"}', two_months_ago)

        skyscraper.archive.archive_old_files(tmpdir)

        assert os.path.isfile(os.path.join(tmpdir, last_month_file))
        assert os.path.isfile(os.path.join(tmpdir, two_months_ago_file))

        assert not os.path.isfile(f_21.name)
        assert not os.path.isfile(f_22.name)
        assert not os.path.isfile(f_3.name)

        # The file from this month should still exist
        assert os.path.isfile(f_1.name)
        assert not os.path.isfile(os.path.join(tmpdir, this_month_file))


def test_archive_can_handle_jsonline_input(tmpdir):
    with tempfile.NamedTemporaryFile(dir=tmpdir, delete=False) as f_1, \
            tempfile.NamedTemporaryFile(dir=tmpdir, delete=False) as f_2:

        today = datetime.datetime.today()
        # use 28, because the shortest month is 28 days. Jumping 30 days back
        # we might possibly get a date from January if it's March 1st
        last_month = datetime.datetime(today.year, today.month, 15) \
            - datetime.timedelta(days=28)
        last_month_file = last_month.strftime('%Y-%m.jl.gz')

        write_file_with_date(
            f_1, '{"foo": "data_11"}\n{"foo": "data_12"}', last_month)
        write_file_with_date(f_2, '{"foo": "data_2"}', last_month)

        skyscraper.archive.archive_old_files(tmpdir)

        last_month_filepath = os.path.join(tmpdir, last_month_file)

        assert os.path.isfile(last_month_filepath)

        assert not os.path.isfile(f_1.name)
        assert not os.path.isfile(f_2.name)

    # File should contain three lines with the content
    with gzip.open(last_month_filepath, 'rt') as f:
        lines = f.readlines()
        lines = list(map(str.strip, lines))

        assert len(lines) == 3
        assert '{"foo": "data_11"}' in lines
        assert '{"foo": "data_12"}' in lines
        assert '{"foo": "data_2"}' in lines
