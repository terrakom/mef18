var mef18 = {
    GREY_CIRCLE: '/static/mef18/images/grey_circle.png',
    GREEN_CIRCLE: '/static/mef18/images/green_circle.png',
    GREEN_CIRCLE_ARROW_IN: '/static/mef18/images/green_circle_arrow_in.png',
    GREEN_CIRCLE_ARROW_OUT: '/static/mef18/images/green_circle_arrow_out.png',
    YELLOW_ARROW: '/static/mef18/images/green_circle_yellow_arrow.png',
    NET_OPTS: {
        width: '100%',
        height: '100%',
        autoResize: true,
        nodes: {
            shape: 'image',
            image: '/static/mef18/images/grey_circle.png',
            font: {
                background: 'white',
                multi: true,
            },
            color: {border: '#808080'},
        },
        edges: {
            width: 7,
            color: '#808080',
            smooth: {
              type: "continuous",
              forceDirection: "none"
            },
        },
        physics: false,
        interaction: {
            dragNodes: false,// do not allow dragging nodes
            zoomView: true,
            dragView: true,
            selectable: false,
            hover: false,
        },
    },
    NET_CENTER: {
        position: {x: 0, y: 0},
        offset: {x: -1000/2, y: -600/2},
        scale: 1,
    },
    NET1: {
        ref: null,
        title: 'Auto Discovery and Zero Touch Configuration of Fixed Wireless Access Devices',
        base_data: {
            nodes: [
                {id: 1, label: 'TRU Device\nTurned UP',
                    x:0, y:0},
                {id: 2, label: 'TRU Initial Discovery',
                    x:100, y:100},
                {id: 3, label: 'TRU Day 1\nConfiguration',
                    x:100, y:250},
                {id: 7, label: 'CPE Inital Discovery',
                    x:450, y:100},
                {id: 4, label: 'TRU Enabled @ AAI',
                    x:350, y:250},
                {id: 8, label: 'CPE Day 1\nConfiguration',
                    x:800, y:250},
                {id: 9, label: 'CPE Enabled @ AAI',
                    x:550, y:250},
                {id: 5, label: 'TRU Mediation Creation',
                    x:100, y:400},
                {id: 6, label: 'TRU Discovered @ SDN-L',
                    x:350, y:400},
                {id: 10, label: 'CPE Mediation Creation',
                    x:800, y:400},
                {id: 11, label: 'CPE Discovered @ SDN-L',
                    x:550, y:400},
                {id: 90, shape:'image', image: '/static/mef18/images/TRU-02.png', size: 50,
                    x:200, y:35},
                {id: 91, shape:'image', image: '/static/mef18/images/CPE-01.png', size: 28,
                    x:500, y:50},
                {id: 92, shape:'image', image: '/static/mef18/images/ONAP.JPG', size: 30,
                    x:450, y:330},

            ],
            edges: [
                {from: 1, to: 2},
                {from: 2, to: 3},
                {from: 3, to: 7, "smooth": {"type": "curvedCW", "roundness": 0.2,}},
                {from: 3, to: 4},
                {from: 3, to: 5},
                {from: 7, to: 8, "smooth": {"type": "curvedCW", "roundness": 0.2,}},
                {from: 9, to: 4, dashes: true, width: 3},
                {from: 8, to: 9},
                {from: 8, to: 10},
                {from: 5, to: 6},
                {from: 10, to: 11},
            ],
        }
    },
    NET2: {
        ref: null,
        title: 'Closed Loop Bandwdith Upgrade/Downgrade',
        base_data: {
            nodes: [
                {id: 12, label: 'Report BW to DCAE',
                    x:400, y:300},
                {id: 13, label: 'DCAE detected crossing\nhigh threshold',
                    x:450, y:100},
                {id: 14, label: 'Send BW upgrade to policy',
                    x:650, y:100},
                {id: 15, label: 'Policy req SO\nto upgrade BW',
                    x:700, y:250},
                {id: 16, label: 'SO trigger SDN-L API\nvia SDN-C to upgrade BW',
                    x:650, y:400},
                {id: 17, label: 'BW upgraded on TRU',
                    x:450, y:400},
                {id: 18, label: 'DCAE detected crossing\nlow threshold',
                    x:350, y:200},
                {id: 19, label: 'Send BW downgrade to policy',
                    x:150, y:200},
                {id: 20, label: 'Policy req SO\nto downgrade BW',
                    x:100, y:350},
                {id: 21, label: 'SO trigger SDN-L API\nvia SDN-C to downgrade BW',
                    x:150, y:500},
                {id: 22, label: 'BW downgraded on TRU',
                    x:350, y:500},
            ],
            edges: [
                {from: 13, to: 12},
                {from: 13, to: 14},
                {from: 14, to: 15},
                {from: 15, to: 16, "smooth": {"type": "curvedCW", "roundness": 0.2,}},
                {from: 16, to: 17},
                {from: 17, to: 12},
                {from: 18, to: 12},
                {from: 18, to: 19},
                {from: 19, to: 20},
                {from: 20, to: 21, "smooth": {"type": "vertical",}},
                {from: 21, to: 22},
                {from: 22, to: 12},
            ],
        }
    },
    BW_OPTS: {
        minValue: 0,
        maxValue: 1000,
        units: 'Kbps',
        majorTicks: [
            '0','200','400','600','800','1000',
        ],
        minorTicks: 2,
        highlights: [
            {
                "from": 800,
                "to": 1000,
                "color": '#cce5ce',
            },
        ],
        strokeTicks: true,
        colorPlate: '#FFFFFF',
        height: 200,
        width: 200,
        valueBox: true,
        animationRule: 'bounce',
        animationDuration: 500,
        value: 0,
        borders: false,
        borderShadowWidth: 0,
        needleCircleInner: false,
        title: 'Bandwidth',
        colorTitle: 'black',
        colorUnits: 'black',
    },
    BW: {
        ref: null,
    },

    gen_bw: function(bw_data){
        var target = document.getElementById('bw_diagram'); // your canvas element
        mef18.BW_OPTS.renderTo = target;
        var gauge = new RadialGauge(mef18.BW_OPTS);
        gauge.draw();
        mef18.BW.ref = gauge;
        mef18.update_bandwidth_diagram(bw_data);
        mef18.resize_bw_diagram();
    },

    gen_net: function(state_data){
        // create an array with nodes
        var nodes = new vis.DataSet(mef18.NET1.base_data.nodes);
        // create an array with edges
        var edges = new vis.DataSet(mef18.NET1.base_data.edges);
        // create a network
        var container = document.getElementById('state_diagram');
        // provide the data in the vis format
        var data = {
            nodes: nodes,
            edges: edges
        };

        // initialize
        var network = new vis.Network(container, data, mef18.NET_OPTS);
        //network.moveTo(mef18.NET_CENTER);
        mef18.NET1.ref = network;
        // diagram 2

        // create an array with nodes
        var nodes2 = new vis.DataSet(mef18.NET2.base_data.nodes);
        // create an array with edges
        var edges2 = new vis.DataSet(mef18.NET2.base_data.edges);
        // create a network
        var container2 = document.getElementById('state_diagram2');
        // provide the data in the vis format
        var data2 = {
            nodes: nodes2,
            edges: edges2
        };

        // initialize
        var network2 = new vis.Network(container2, data2, mef18.NET_OPTS);
        //network2.moveTo(mef18.NET_CENTER);
        mef18.NET2.ref = network2;

        // activate states according to state_data
        mef18.NET1.ref.body.data.nodes.update({id: 1, image: mef18.GREEN_CIRCLE, color: {border: 'green'}});
        var diagram = mef18.update_state_diagrams(state_data);
        // Change which state diagram is initially active based on nodes

        network.on('click', mef18.click_network);
        network2.on('click', mef18.click_network);
        $('#state_diagram').parent().parent().addClass('active');
        $('#state_diagram2').parent().parent().removeClass('active');
        mef18.update_state_diagram_title();
    },

    click_network: function(properties){
        console.log('click_network', properties, properties.nodes);
    },

    gen_update_functions: function(){
        // update function
        window.setInterval(function(){
            if (katana.$activeTab.find('#state_diagram').length) {
                var csrf = katana.$activeTab.find('.csrf-container input').val();
                var url = 'mef18/states';
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!this.crossDomain)
                            xhr.setRequestHeader("X-CSRFToken", csrf);
                    }
                });
                $.ajax({
                    url: url,
                    type: "GET",
                }).done(function(response) {
                    var states = response.states;
                    var diagram = mef18.update_state_diagrams(states);
                }).fail(function(response) {
                    console.log('refresh failure', response);
                });

                url = 'mef18/bandwidth';
                $.ajaxSetup({
                    beforeSend: function(xhr, settings) {
                        if (!this.crossDomain)
                            xhr.setRequestHeader("X-CSRFToken", csrf);
                    }
                });
                $.ajax({
                    url: url,
                    type: "GET",
                }).done(function(response) {
                    mef18.update_bandwidth_diagram(response.bw);
                }).fail(function(response) {
                    console.log('refresh failure', response);
                });

                url = 'mef18/status';
                $.ajax({
                    url: url,
                    type: "GET",
                }).done(function(response){
                    console.log('status check failed');
                    mef18.enable_activate_service_button(response.status == 'IDLE');
                    mef18.enable_deactivate_service_button(response.status == 'IDLE');
                }).fail(function(response){
                    console.log('status check failed');
                    mef18.enable_activate_service_button(true);
                    mef18.enable_deactivate_service_button(true);
                });

            } else {
                window.clearInterval();
            }
        }, 2000);
        // on slide function
        $('#carousel-example-generic').on('slid.bs.carousel', function(){
            mef18.resize_bw_diagram();
            mef18.update_state_diagram_title();
        });
        window.addEventListener("resize", mef18.resize_bw_diagram);
    },

    resize_bw_diagram: function(){
        var bw = $('#bw_diagram');
        var parent = bw.parent();
        var w = parent.width();
        var h = parent.height();
        if (w > 0 && h > 0) {
            mef18.BW.ref.update({width:w, height:h});
        }
    },

    update_state_diagram_title: function(){
        if ($('#state_diagram').parent().parent().hasClass('active')) {
            $('#mef18-state-diagram-title').text(mef18.NET1.title);
        } else {
            $('#mef18-state-diagram-title').text(mef18.NET2.title);
        }
    },

    update_state_diagrams: function(states){
        var diagram = 1;
        mef18.NET1.ref.body.data.nodes.getIds().forEach(function(id){
            if (states.indexOf(id) >= 0) {
                mef18.NET1.ref.body.data.nodes.update({id: id, image: mef18.GREEN_CIRCLE, color: {border: 'green'}});
            } else if (id > 0 && id < 12) {
                mef18.NET1.ref.body.data.nodes.update({id: id, image: mef18.GREY_CIRCLE, color: {border: '#808080'}});
            }
        });
        mef18.NET2.ref.body.data.nodes.getIds().forEach(function(id){
            if (states.indexOf(id) >= 0) {
                mef18.NET2.ref.body.data.nodes.update({id: id, image: mef18.GREEN_CIRCLE, color: {border: 'green'}});
            } else if (id > 11 && id < 23) {
                mef18.NET2.ref.body.data.nodes.update({id: id, image: mef18.GREY_CIRCLE, color: {border: '#808080'}});
            }
        });
        return diagram;
    },

    update_bandwidth_diagram: function(bw){
        if (bw < 0) {bw = 0;}
        mef18.BW.ref.update({
            minValue: 0,
            maxValue: 100,
            units: 'Mbps',
            majorTicks: [
                '0','25','50','75','100',
            ],
            minorTicks: 5,
            highlights: [
                {
                    "from": 0,
                    "to": 20,
                    "color": '#f1c40f',
                },
                {
                    "from": 50,
                    "to": 75,
                    "color": '#cce5ce',
                },
                {
                    "from": 75,
                    "to": 100,
                    "color": '#66b26c',
                },
            ],
        });
        mef18.BW.ref.value = (bw / 1000000);
    },

    kafka_delete: function(){
        var button = this;
        var rowId = button.val();
        var elem = $('#'+rowId).children();
        var settings = elem.map(function(){
            return $(this).text();
        });
        // Open alert to confirm deletion of the consumer + warning message that states seen will be kept as is
        katana.openAlert({
            alert_type: 'warning',
            heading: 'Confirm delete',
            text: 'Deleting Kafka consumer ' + rowId + '.',
        }, function(response){
            data = {id:settings[0]};
            var csrf = katana.$activeTab.find('.csrf-container input').val();
            var url = 'mef18/kafka_consumers';
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain)
                        xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            });
            $.ajax({
                url: url,
                type: "DELETE",
                data: data,
            }).done(function(response) {
                mef18.kafka_refresh();
            }).fail(function(response) {
                console.log('deletion failure', response);
                katana.openAlert({
                    alert_type: 'danger',
                    heading: 'ERROR',
                    text: 'Kafka consumer could not be deleted',
                    'show_cancel_btn': false,
                });
                mef18.kafka_refresh();
            });
        }, function(response){});
    },

    kafka_add: function(){
        var elem = $('#mef18-kafka-new-consumer-add');
        var input = elem.find('input');
        var settings = {};
        input.map(function(){
            var v = $(this).val();
            var k = $(this).attr('key');
            if (k == 'topics') {
                if (v.match(/,/)) {v = v.split(/,/).map(function(item){return item.trim()});}
                else {v = [v];}
            }
            settings[k] = v;
        });
        katana.openAlert({
            alert_type: 'warning',
            heading: 'Confirm creation',
            text: 'Creating Kafka consumer ' + settings.id + '.',
        }, function(response){
            data = settings;
            var csrf = katana.$activeTab.find('.csrf-container input').val();
            var url = 'mef18/kafka_consumers';
            $.ajaxSetup({
                beforeSend: function(xhr, settings) {
                    if (!this.crossDomain)
                        xhr.setRequestHeader("X-CSRFToken", csrf);
                }
            });
            $.ajax({
                url: url,
                type: "POST",
                data: JSON.stringify(settings),
                contentType: 'application/json'
            }).done(function(response) {
                mef18.kafka_refresh();
            }).fail(function(response) {
                katana.openAlert({
                    alert_type: 'danger',
                    heading: 'ERROR',
                    text: 'Kafka consumer could not be added',
                    'show_cancel_btn': false,
                });
                mef18.kafka_refresh();
            });
        }, function(response){});
    },

    kafka_refresh: function(){
        var csrf = katana.$activeTab.find('.csrf-container input').val();
        var url = 'mef18/kafka_consumers';
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain)
                    xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        });
        $.ajax({
            url: url,
            type: "GET",
            contentType: 'application/json'
        }).done(function(response) {
            var tbody = $('#mef18-kafka-consumer-table-body');
            tbody.empty();
            for (var id in response.settings) {
                var row = $('<tr id="mef18-kafka-consumer-' + id + '">'
                            + '<th scope="row">' + id + '</th>'
                            + '<td>' + response.settings[id].server + '</td>'
                            + '<td>' + response.settings[id].group_id + '</td>'
                            + '<td>' + response.settings[id].topics.join(", ") + '</td>'
                            + '<td>'
                            + '    <button type="button" class="btn btn-success" katana-click="mef18.kafka_delete" value="mef18-kafka-consumer-' + id + '">Delete</button>'
                            + '</td>'
                            + '</tr>');
                tbody.append(row);
            }
            row = $('<tr id="mef18-kafka-new-consumer-add">'
                    + '<th scope="row"><input type="text" class="form-control" key="id" value=""></th>'
                    + '<td><input type="text" class="form-control" key="server" value=""></td>'
                    + '<td><input type="text" class="form-control" key="group_id" value=""></td>'
                    + '<td><input type="text" class="form-control" key="topics" value=""></td>'
                    + '<td><button type="button" class="btn btn-success" katana-click="mef18.kafka_add">Add</button></td>'
                    + '</tr>');
            tbody.append(row);
        }).fail(function(response) {
            console.log('fail', response);
        });
    },

    reset_states: function(){
        var csrf = katana.$activeTab.find('.csrf-container input').val();
        var url = 'mef18/states';
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain)
                    xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        });
        $.ajax({
            url: url,
            type: "DELETE",
        }).done(function(response) {
            mef18.update_state_diagrams(response.states);
        }).fail(function(response) {
            console.log('failed to delete states', response);
        });
    },

    activate_service: function(){
        var csrf = katana.$activeTab.find('.csrf-container input').val();
        var url = 'mef18/activate';
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain)
                    xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        });
        mef18.enable_activate_service_button(false);
        $.ajax({
            url: url,
            type: "POST",
        }).done(function(response) {
            console.log('MEF18 Service Activated');
        }).fail(function(response) {
            console.log('failed to activate service', response);
            mef18.enable_activate_service_button(true);
        });
    },

    deactivate_service: function(){
        var csrf = katana.$activeTab.find('.csrf-container input').val();
        var url = 'mef18/deactivate';
        $.ajaxSetup({
            beforeSend: function(xhr, settings) {
                if (!this.crossDomain)
                    xhr.setRequestHeader("X-CSRFToken", csrf);
            }
        });
        mef18.enable_activate_service_button(false);
        $.ajax({
            url: url,
            type: "POST",
        }).done(function(response) {
            console.log('MEF18 Service De-activated');
        }).fail(function(response) {
            console.log('failed to de-activate service', response);
            mef18.enable_activate_service_button(true);
        });
    },

    enable_activate_service_button: function(enable){
        if (enable) {
            $('#mef18-service-activate').prop('disabled', false);
            $('#mef18-service-activate').text('Activate');
        } else {
            $('#mef18-service-activate').prop('disabled', true);
            $('#mef18-service-activate').text('Pending...');
        }
    },

    enable_deactivate_service_button: function(enable){
        if (enable) {
            $('#mef18-service-deactivate').prop('disabled', false);
            $('#mef18-service-deactivate').text('De-activate');
        } else {
            $('#mef18-service-deactivate').prop('disabled', true);
            $('#mef18-service-deactivate').text('Pending...');
        }
    },
}
