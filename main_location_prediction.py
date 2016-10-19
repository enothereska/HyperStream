# The MIT License (MIT) # Copyright (c) 2014-2017 University of Bristol
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
#  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
#  MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
#  IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
#  DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
#  OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#  OR OTHER DEALINGS IN THE SOFTWARE.

import itertools
import logging

from hyperstream import HyperStream, TimeInterval

from sphere_helpers import PredefinedTools, scripted_experiments, second, minute, hour


# Analysis of data from:
# http://10.70.18.138/data_viewer/scripted/001/2/Location/
# Experiment id: 001   Start: 2015-08-06T13:35:36.035000Z   End: 2015-08-06T14:12:22.008000Z
# Offsets: 0:01:06, 0:01:06, 0:01:06   Annotators: 2, 3, 5
# Annotation files: [ S1060001_jdl.eaf | S1060001_ac.eaf | S1060001_ks.eaf ]
# Mongo query: db.annotations.find({tier: 'Location', start: {$gt: ISODate('2015-08-06T13:35:36.035000Z')},
# end: {$lte: ISODate('2015-08-06T14:12:22.008000Z')}})

if __name__ == '__main__':
    # TODO: hyperstream needs it's own logger (can be a clone of this one)
    hyperstream = HyperStream()

    tools = PredefinedTools(hyperstream.channel_manager)

    # Various channel managers
    M = hyperstream.channel_manager.memory
    S = hyperstream.channel_manager.sphere
    T = hyperstream.channel_manager.tools
    D = hyperstream.channel_manager.mongo

    # Dictionary to hold nodes
    N = {}

    # Create a simple one step workflow for querying
    w = hyperstream.create_workflow(
        workflow_id="localisation",
        name="Test of localisation",
        owner="TD",
        description="Would like to test localisation using PIR and RSS, so we need to first get the appropriate data"
                    "out of the SPHERE stream, with the appropriate meta-data attached, and then use a model")

    # Some plate values for display purposes
    h1 = (('house', '1'),)
    wA = (('wearable', 'A'),)
    locs = tuple(("location", loc) for loc in ["kitchen", "hallway", "lounge"])
    eids = tuple(("scripted", i + 1) for i in range(0, len(scripted_experiments.intervals)))

    locs_eids = tuple(itertools.product(locs, eids))
    print(locs_eids)

    # get a dict of experiment_id => annotator_id mappings
    experiment_id_to_annotator_ids = dict(
        (k, [a['data'] for a in g])
        for k, g in itertools.groupby(
            (m for m in hyperstream.config.meta_data if 'tag' in m and m['tag'] == 'annotator'),
            lambda x: x['identifier'].split('.')[1].split('_')[1]))

    # time_interval = scripted_experiments.span
    time_interval = TimeInterval(scripted_experiments.intervals[0].start,
                                 scripted_experiments.intervals[0].start + second)

    # Here we used the splitter tool over the RSS data to generate the plate
    N["rss_flat"] = w.create_node(stream_name="rss", channel=S, plate_ids=["H1"])
    w.create_factor(tool=tools.wearable_rss, sources=None, sink=N["rss_flat"])

    N["rss_aid"] = w.create_node(stream_name="rss_aid", channel=M, plate_ids=["H1.L"])
    w.create_multi_output_factor(tool=tools.split_aid, source=N["rss_flat"], sink=N["rss_aid"])

    N["rss_aid_uid"] = w.create_node(stream_name="rss_aid_uid", channel=M, plate_ids=["H1.L.W"])
    w.create_multi_output_factor(tool=tools.split_uid, source=N["rss_aid"], sink=N["rss_aid_uid"])

    N["rss"] = w.create_node(stream_name="rss", channel=D, plate_ids=["H1.L.W"])
    w.create_factor(tool=tools.wearable_rss_values, sources=[N["rss_aid_uid"]], sink=N["rss"])

    # Now we want to split by time interval onto a time-oriented plate
    N["rss_time"] = w.create_node(stream_name="rss_time", channel=M, plate_ids=["H1.L.W", "H1.scripted"])
    # N["rss_time"] = w.create_node(stream_name="rss_time", channel=M, plate_ids=["H.L", "H.scripted"])
    f = w.create_multi_output_factor(tool=tools.split_time, source=N["rss"], sink=N["rss_time"])
    f.execute(scripted_experiments.intervals[0] + (-1, 0))

    w.execute(time_interval)

    # N["rss_flat"].print_head(None, h1, time_interval)
    # N["rss_aid"].print_head(h1, locs, time_interval)
    # N["rss_aid_uid"].print_head(w1, locs, time_interval)
    N["rss"].print_head(h1 + wA, locs, time_interval)
    N["rss_time"].print_head(h1 + wA, locs_eids, time_interval)

    exit(0)

    # TODO just two for now
    # for i, (time_interval, annotator_ids) in enumerate(scripted_experiments[:2]):
    for i, time_interval in enumerate(scripted_experiments[:2]):
        time_interval.end = time_interval.start + minute

        experiment_id = str(i + 1)
        annotator_ids = experiment_id_to_annotator_ids[experiment_id]
        anns = [("annotator", ann) for ann in annotator_ids]

        hyperstream.plate_manager.create_plate(
            plate_id="H1.scripted_{}".format(experiment_id),
            description="Annotators for scripted experiment {} in SPHERE house".format(experiment_id),
            meta_data_id="annotator",
            values=[],
            complement=True,
            parent_plate="H1.scripted"
        )

        if False:
            # Load in annotations from the same time period
            N["annotations_flat"] = w.create_node(stream_name="annotations_flat", channel=M, plate_ids=["H1.scripted"])

            annotations_location = hyperstream.channel_manager.get_tool(
                name="sphere",
                parameters=dict(modality="annotations", annotators=annotator_ids, elements={"Location"},
                                filters={"trigger": 1})
            )

            w.create_factor(
                tool=annotations_location, sources=None, sink=N["annotations_flat"]).execute(time_interval) \
                .sink.print_head(None, (("house", "1"), ('scripted', str(i + 1))), time_interval)

            plate_id = "H1.scripted_{}".format(i + 1)
            # Put these on to an annotators plate
            N["annotations_split"] = w.create_node(stream_name="annotations_split", channel=M, plate_ids=[plate_id])
            w.create_multi_output_factor(
                tool=tools.split_annotator, source=N["annotations_flat"], sink=N["annotations_split"]).execute(time_interval)
            N["annotations_split"].print_head(h1, anns, time_interval)

            # Pull out the label
            N["annotations"] = w.create_node(stream_name="annotations", channel=M, plate_ids=[plate_id])
            w.create_factor(tool=tools.annotations_label, sources=[N["annotations_split"]],
                            sink=N["annotations"]).execute(time_interval)
            N["annotations"].print_head(h1, anns, time_interval)

        # Here we used the splitter tool over the RSS data to generate the plate
        N["rss_flat"] = w.create_node(stream_name="rss", channel=S, plate_ids=["H1"])
        w.create_factor(tool=tools.wearable_rss, sources=None, sink=N["rss_flat"]).execute(time_interval)
        N["rss_flat"].print_head(None, h1, time_interval)

        N["rss_aid"] = w.create_node(stream_name="rss_aid", channel=M, plate_ids=["H1.L"])
        w.create_multi_output_factor(tool=tools.split_aid, source=N["rss_flat"], sink=N["rss_aid"]).execute(time_interval)
        N["rss_aid"].print_head(h1, locs, time_interval)

        N["rss_aid_uid"] = w.create_node(stream_name="rss_aid_uid", channel=M, plate_ids=["H1.L.W"])
        w.create_multi_output_factor(tool=tools.split_uid, source=N["rss_aid"], sink=N["rss_aid_uid"]).execute(time_interval)
        N["rss_aid_uid"].print_head(h1 + wA, locs, time_interval)

        N["rss"] = w.create_node(stream_name="rss", channel=D, plate_ids=["H1.L.W"])
        w.create_factor(tool=tools.wearable_rss_values, sources=[N["rss_aid_uid"]],
                        sink=N["rss"], alignment_node=None).execute(time_interval)
        N["rss"].print_head(h1 + wA, locs, time_interval)

    exit(0)

    # PIR sensor plate

    # Stream to get motion sensor data
    N["pir"] = w.create_node(stream_name="environmental_db", channel=D, plate_ids=["H1"])
    f_pir = w.create_factor(tool=tools.environmental_motion, sources=None, sink=N["pir"], alignment_node=None)

    # Execute the workflow
    w.execute(time_interval)

    print(N["pir"].streams[('house', '1'), ].window(time_interval).values()[0:5])
    print(N["rss_aid"].streams[('house', '1'), ].window(time_interval).values()[0:5])
