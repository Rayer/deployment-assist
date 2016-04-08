from P4 import P4, P4Exception
import datetime
import sys

p4 = P4()
p4.port = "172.17.17.14:1666"
p4.user = "dora.yang"

source_p4_client = "dora.yang_ubuntu"
private_build_p4_client = "dora.yang_private_build"
unproc_cls = [436505]
shelved_cls = [424009, 436505]


def colored_str(wording, color=None):
    if color is None:
        color = "default"

    color_map = {
        'red': "\033[91m{}\033[00m",
        'cyan': "\033[96m{}\033[00m",
        'green': "\033[92m{}\033[00m",
        'black': "\033[98m{}\033[00m",
        'yellow': "\033[93m{}\033[00m",
        'default': "{}"
    }
    return color_map[color].format(wording)


def check_cl_no(check_list):
    error_msg_list = []
    cl_err_list = []
    shelved_file_err = []
    shelved_cls = []
    for check_cl in check_list:
        try:
            # open_result = p4.run("opened", "-c", check_cl)
            desc_result = p4.run("describe", "-S", check_cl)
            if desc_result[0]['status'] != "pending":
                raise Exception("{0:<6} is not pending changelist".format(check_cl))
            shelved_file_info = desc_result[0]
            for idx in xrange(len(shelved_file_info['depotFile'])):
                last_version = p4.run("files", shelved_file_info['depotFile'][idx])[0]['rev']
                if last_version != shelved_file_info['rev'][idx]:
                    shelved_file_err.append("     {0:<16}        {1:<16}    {2}"
                                            .format(colored_str(shelved_file_info['rev'][idx], 'red'),
                                                    colored_str(last_version, 'cyan'),
                                                    shelved_file_info['depotFile'][idx]))
                else:
                    shelved_cls.append(check_cl)

        except P4Exception as p4e:
            cl_err_list.append(p4e.warnings[0])
        except Exception as e:
            cl_err_list.append(e.message)

    if len(cl_err_list) > 0:
        error_msg_list.append("CL# error as below:\n" + "\n".join(map(str, cl_err_list)) + "\n")

    if len(shelved_file_err) > 0:
        error_msg_list.append("File version does not match as below:\n -> Shelved# V.S. Latest# - File info \n" +
                              "\n".join(map(str, shelved_file_err)))

    if len(error_msg_list) > 0:
        raise Exception("\n".join(map(str, error_msg_list)))

    shelved_cls = list(set([x for x in shelved_cls if shelved_cls.count(x) > 1]))
    return shelved_cls


def sync_control():
    sync_folder = "//depot/scg/control_plane/control/"
    before_datetime = datetime.datetime.utcnow()
    print("***** start sync ({0})".format(before_datetime))
    sync_result = p4.run("sync", "-f", sync_folder + "...")
    # for sync_info in sync_result:
    #     print("#{:<5} {}".format(colored_str(sync_info['rev'], "green"), sync_info['depotFile']))
    # p4.run("sync", sync_folder + "...#head")
    after_datetime = datetime.datetime.utcnow()
    print("***** end sync ({0}): {1} secs.)".format(after_datetime, (after_datetime - before_datetime).total_seconds()))


def shelve_cl_list(cl_list):
    p4.client = source_p4_client
    for cl in cl_list:
        p4.run_shelve("-c", cl, "-f")


def get_new_cl_no(source_cl):
    p4.client = private_build_p4_client
    new_cl = p4.fetch_change()
    new_cl._description = "Unshelve CL# {0} files".format(source_cl)
    new_cl_no = p4.save_change(new_cl)[0].split( )[1]
    return new_cl_no


def unshelve_cl_list(cl_list):
    new_cl_list = []
    for source_cl in cl_list:
        new_clno = get_new_cl_no(source_cl)  # create new CL
        print("new CL# : {0}".format(new_clno))
        new_cl_list.insert(len(new_cl_list), new_clno)
        p4.run_unshelve('-s', source_cl, '-f', "-c", new_clno)  # unshelve CL
    return new_cl_list


def revert_delete_cl(cl_list):
    for revert_cl in cl_list:
        print("revert cl : {0}".format(revert_cl))
        opened_list = p4.run("opened", "-c", revert_cl)
        if len(opened_list) > 0:
            for cl in opened_list:
                p4.run("revert", cl['clientFile'])  # revert file in CL
                print(" - {0}".format(cl['clientFile']))
        p4.run("change", "-d", revert_cl)  # delete CL


def get_p4_info():
    info = p4.run("info")
    for key in info[0]:
        print key, "=", info[0][key]


def get_pending_cl_list(show_cl_info=False,p4_client=None):
    if p4_client is None:
        p4_client = private_build_p4_client

    changes = p4.run("changes", "-s", "pending", "-u", p4.user, "-c", p4_client)
    change_list = []
    for cl in changes:
        change_list.append(cl['change'])
        if show_cl_info:
            print("{0:>6} - {1}".format(cl['change'], cl['desc'].replace("\n", " ")))

    return change_list


def show_p4_client_info():
    clientspec = p4.fetch_client()
    print(clientspec)


def main():
    try:  # Catch exceptions with try/except
        # 0 - connect
        p4.connect()  # Connect to the Perforce Server
        p4.client = private_build_p4_client

        print("----------------------------------------------------")
        # 1 - revert and delete CL
        revert_delete_cl(get_pending_cl_list())
        get_pending_cl_list(True)

        # 2 - CL# check
        shelved_cls = check_cl_no([436505])

        print("----------------------------------------------------")
        # 3 - sync code
        sync_control()

        # 4 - shelve CL
        # shelve_cl_list(unproc_cls)

        print("----------------------------------------------------")
        # 5 - unshelve CL
        unshelve_cl_list(shelved_cls)

        p4.disconnect()                # Disconnect from the Server

    except P4Exception:
        for e in p4.errors:  # Display errors
            print e
    except Exception as e:
        print(e.message)

if __name__ == '__main__':
    main()